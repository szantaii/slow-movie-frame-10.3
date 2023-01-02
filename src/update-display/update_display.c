#include "update_display.h"

#include "../../vendor/IT8951-ePaper/Raspberry/lib/GUI/GUI_Paint.h"
#include "../../vendor/IT8951-ePaper/Raspberry/lib/GUI/GUI_BMPfile.h"

#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <sys/stat.h>
#include <endian.h>
#include <string.h>
#include <math.h>

extern uint8_t INIT_Mode;
extern uint8_t GC16_Mode;

void print_help(void)
{
    fprintf(
        stdout,

        "%s\n"
        "%s\n"
        "%s\n"
        "%s\n\n"

        "%s\n"
        "%s\n"
        "%s\n"
        "%s\n\n"

        "%s\n"
        "%s\n"
        "%s\n"
        "%s\n\n"

        "%s\n"
        "%s\n"
        "%s\n"
        "%s\n"
        "%s\n"
        "%s\n"
        "%s\n\n"

        "%s\n"
        "%s\n"
        "%s\n"
        "%s\n"
        "%s\n\n",

        "Usage: update-display -v VOLTAGE [-f <IMAGE_FILE> | -h]",
        "Update the display of the connected 10.3 e-paper device either",
        "by clearing it or drawing a 8bit per channel RGB BMP or a custom",
        "4bits per pixel image on it.",

        "Mandatory option:",
        "  -v VOLTAGE  use the VOLTAGE for the connected e-paper device",
        "              (Read and use the exact voltage from the flexible",
        "              printed circuit cable of the connected device.)",

        "Optional options:",
        "  -f IMAGE_FILE  draw the specified image on the display of the",
        "                 connected e-paper device",
        "  -h             display this help and exit",

        "Exit status:",
        "  0  success",
        "  1  wrong command-line arguments or command-line parsing error",
        "  2  failed to initialize bcm2835 device",
        "  3  the connected device is not a 10.3 inch e-paper device",
        "  4  error during drawing BMP/4BPP image onto display",
        "  5  unsupported image file format",

        "Examples:",
        "  ./update-display -h",
        "  ./update-display -v -2.51",
        "  ./update-display -v -1.50 -f /path/to/image.bmp",
        "  ./update-display -v -1.48 -f /path/to/image.4bpp");
}

int str_ends_with(const char *str, const char *substr)
{
    if (str == NULL || substr == NULL)
    {
        return -1;
    }

    size_t str_length = strlen(str);
    size_t substr_length = strlen(substr);

    if (str_length >= substr_length
        && strcmp(str + (str_length - substr_length), substr) == 0)
    {
        return 0;
    }

    return 1;
}

int display_bmp_image(
    IT8951_Dev_Info device_info,
    uint32_t target_memory_address,
    const char *file_path)
{
    const uint8_t bits_per_pixel = 8;
    uint8_t *image = NULL;
    size_t image_size = (size_t)device_info.Panel_W * (size_t)device_info.Panel_H;

    if (file_path == NULL)
    {
        fprintf(stderr, "%s\n", "Received null pointer for file path.");

        return -1;
    }

    if ((image = (uint8_t *)malloc(image_size)) == NULL)
    {
        fprintf(
            stderr,
            "%s (%zu bytes).\n",
            "Cannot allocate enough memory for image buffer",
            image_size);

        return -2;
    }

    Paint_NewImage(image, device_info.Panel_W, device_info.Panel_H, 0, BLACK);
    Paint_SelectImage(image);
    Paint_SetRotate(ROTATE_0);
    Paint_SetMirroring(MIRROR_HORIZONTAL);
    Paint_SetBitsPerPixel(bits_per_pixel);
    Paint_Clear(WHITE);

    if (GUI_ReadBmp(file_path, 0, 0) != 0)
    {
        fprintf(
            stderr,
            "%s\n",
            "Cannot process BMP image or allocate enough memory.");

        if (image != NULL)
        {
            free(image);
            image = NULL;
        }

        return -3;
    }

    EPD_IT8951_Clear_Refresh(device_info, target_memory_address, GC16_Mode);

    EPD_IT8951_8bp_Refresh(
        image,
        0,
        0,
        device_info.Panel_W,
        device_info.Panel_H,
        true,
        target_memory_address);

    if (image != NULL)
    {
        free(image);
        image = NULL;
    }

    return 0;
}

int display_4bpp_image(
    IT8951_Dev_Info device_info,
    uint32_t target_memory_address,
    const char *file_path)
{
    struct stat file_status;
    size_t file_size = 0;
    FILE *fp = NULL;
    uint16_t image_width = 0;
    uint16_t image_height = 0;
    size_t image_data_size = 0;
    uint8_t *image_data = NULL;
    size_t image_header_size = sizeof(image_width) + sizeof(image_height);
    uint16_t maximum_resolution = (uint16_t)(pow(2.0, 16.0) - 1.0);

    if (file_path == NULL)
    {
        fprintf(
            stderr,
            "%s\n",
            "Received null pointer for file path.");

        return -1;
    }

    if (stat(file_path, &file_status) != 0)
    {
        fprintf(
            stderr,
            "%s (%s).\n",
            "Unable to get file status",
            file_path);

        return -2;
    }

    file_size = (size_t)file_status.st_size;

    if (file_size < image_header_size)
    {
        fprintf(
            stderr,
            "%s (%s).\n",
            "File size is smaller than the minimum size of a 4bpp image",
            file_path);

        return -3;
    }

    if (file_size == image_header_size)
    {
        EPD_IT8951_Clear_Refresh(device_info, target_memory_address, INIT_Mode);

        fprintf(
            stderr,
            "%s (%s).\n",
            "No image data in file, not drawing anything to display",
            file_path);

        return 0;
    }

    fp = fopen(file_path, "rb");

    if (fp == NULL)
    {
        fprintf(
            stderr,
            "%s (%s).\n",
            "Cannot open file",
            file_path);

        return -4;
    }

    if (!(fread(&image_width, sizeof(image_width), 1, fp) == 1
        && fread(&image_height, sizeof(image_height), 1, fp) == 1))
    {
        fclose(fp);

        fprintf(
            stderr,
            "%s (%s).\n",
            "Invalid 4bpp image file",
            file_path);

        return -5;
    }

    image_width = le16toh(image_width);
    image_height = le16toh(image_height);

    if (!((image_width <= maximum_resolution && image_height < maximum_resolution)
        || (image_width < maximum_resolution && image_height <= maximum_resolution)))
    {
        fclose(fp);

        fprintf(
            stderr,
            "%s\n",
            "Image resolution is higher than the maximum allowed "
            "(2^16 - 2 pixels by 2^16 - 1 pixels).");

        return -6;
    }

    if (((image_width * image_height) % 2) != 0)
    {
        fclose(fp);

        fprintf(
            stderr,
            "%s\n",
            "The number of pixels in this 4bpp image is odd! "
            "The number of pixels in a 4bpp image must be even.");

        return -7;
    }

    image_data_size = (image_width * image_height) / 2;

    if (image_width == 0
        ||image_height == 0
        || file_size != image_header_size + image_data_size)
    {
        fclose(fp);

        fprintf(
            stderr,
            "%s (%s).\n",
            "Invalid 4bpp image file",
            file_path);

        return -8;
    }

    image_data = malloc(image_data_size);

    if (image_data == NULL)
    {
        fclose(fp);

        fprintf(
            stderr,
            "%s\n",
            "Cannot allocate enough memory for 4bpp image data.");

        return -9;
    }

    if (fread(image_data, image_data_size, 1, fp) != 1)
    {
        free(image_data);
        image_data = NULL;

        fclose(fp);

        fprintf(
            stderr,
            "%s\n",
            "Failed to read 4bpp image data.");

        return -10;
    }

    fclose(fp);

    EPD_IT8951_Clear_Refresh(device_info, target_memory_address, GC16_Mode);
    EPD_IT8951_4bp_Refresh(
        image_data,
        0,
        0,
        device_info.Panel_W,
        device_info.Panel_H,
        true,
        target_memory_address,
        false);

    if (image_data != NULL)
    {
        free(image_data);
        image_data = NULL;
    }

    return 0;
}
