#include "../../vendor/IT8951-ePaper/Raspberry/lib/Config/DEV_Config.h"
#include "../../vendor/IT8951-ePaper/Raspberry/lib/e-Paper/EPD_IT8951.h"
#include "../../vendor/IT8951-ePaper/Raspberry/lib/GUI/GUI_Paint.h"
#include "../../vendor/IT8951-ePaper/Raspberry/lib/GUI/GUI_BMPfile.h"

#include <stdbool.h>
#include <math.h>
#include <unistd.h>
#include <stdio.h>

void print_help(void);
int display_bmp_image(
    uint16_t width,
    uint16_t height,
    uint32_t target_memory_address,
    const char *file_path);

int main(int argc, char *argv[])
{
    int opt = 0;
    bool display_image = false;
    char *file_path = NULL;
    double tmp_vcom = 0.0;
    uint16_t vcom = 0;
    uint32_t target_memory_address = 0x0;
    IT8951_Dev_Info device_info = {
        0,
        0,
        0,
        0,
        {0, 0, 0, 0, 0, 0, 0, 0},
        {0, 0, 0, 0, 0, 0, 0, 0}};

    while ((opt = getopt(argc, argv, "f:hv:")) != -1)
    {
        switch (opt)
        {
        case 'f':
            file_path = optarg;

            if (file_path == NULL)
            {
                fprintf(
                    stderr,
                    "%s\n",
                    "Specified file path is null pointer somehow!");

                return 1;
            }

            if (access(file_path, F_OK) != 0)
            {
                fprintf(
                    stderr,
                    "%s (%s).\n",
                    "Specified file does not exist or insufficient permissions",
                    file_path);

                return 1;
            }

            display_image = true;

            break;

        case 'h':
            print_help();

            return 0;

        case 'v':
            if (sscanf(optarg, "%lf", &tmp_vcom) != 1 || tmp_vcom == 0.0)
            {
                fprintf(stderr, "%s\n", "Invalid VCOM value specified.");

                return 1;
            }

            vcom = (uint16_t)(fabs(tmp_vcom) * 1000);

            break;

        case '?':
            if (optopt == 'f')
            {
                fprintf(stderr, "%s\n", "No file was specified.");
            }
            else if (optopt == 'v')
            {
                fprintf(stderr, "%s\n", "No VCOM value specified.");
            }

            print_help();

            return 1;

        default:
            fprintf(stderr, "%s\n", "Invalid option.");

            print_help();

            return 1;
        }
    }

    if (DEV_Module_Init() != 0)
    {
        fprintf(stderr, "%s\n", "Failed to initialize bcm2835 device.");

        return 2;
    }

    device_info = EPD_IT8951_Init(vcom);

    if (strcmp((char *)device_info.LUT_Version, "M841_TFA5210") != 0)
    {
        fprintf(
            stderr,
            "%s\n",
            "Connected device is not a 10.3 inch e-paper device.");

        return 3;
    }

    target_memory_address = device_info.Memory_Addr_L | (device_info.Memory_Addr_H << 16);

    EPD_IT8951_Clear_Refresh(device_info, target_memory_address, INIT_Mode);

    if (display_image)
    {
        if (display_bmp_image(device_info.Panel_W, device_info.Panel_H, target_memory_address, file_path) != 0)
        {
            fprintf(
                stderr,
                "%s (%s).\n",
                "Error during drawing BMP image onto screen",
                file_path);

            return 4;
        }
    }

    EPD_IT8951_Sleep();
    DEV_Module_Exit();

    return 0;
}

void print_help(void)
{
    fprintf(
        stdout,

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
        "%s\n",

        "Usage: update-screen -v VOLTAGE [-f <BMP_FILE> | -h]",
        "Update the screen of the connected 10.3 e-paper device either",
        "by clearing it or drawing a 8bit/channel RGB BMP image on it.",

        "Mandatory option:",
        "  -v VOLTAGE  use the VOLTAGE for the connected e-paper device",
        "              (Read and use the exact voltage from the flexible",
        "              printed circuit cable of the connected device.)",

        "Optional options:",
        "  -f BMP_FILE  draw the 8bit/channel RGB BMP_FILE on the screen of",
        "               the connected e-paper device",
        "  -h           display this help and exit",

        "Exit status:",
        "  0  success",
        "  1  wrong command-line arguments or command-line parsing error",
        "  2  failed to initialize bcm2835 device",
        "  3  the connected device is not a 10.3 inch e-paper device",
        "  4  error during drawing BMP image onto screen");
}

int display_bmp_image(
    uint16_t width,
    uint16_t height,
    uint32_t target_memory_address,
    const char *file_path)
{
    const uint8_t bits_per_pixel = 8;
    uint8_t *image = NULL;
    size_t image_size = (size_t)width * (size_t)height;

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

    Paint_NewImage(image, width, height, 0, BLACK);
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
            "Cannot not process BMP image or allocate enough memory.");

        if (image != NULL)
        {
            free(image);
            image = NULL;
        }

        return -3;
    }

    EPD_IT8951_8bp_Refresh(
        image,
        0,
        0,
        width,
        height,
        true,
        target_memory_address);

    if (image != NULL)
    {
        free(image);
        image = NULL;
    }

    return 0;
}
