#include "update_display.h"

#include "../../vendor/IT8951-ePaper/Raspberry/lib/Config/DEV_Config.h"
#include "../../vendor/IT8951-ePaper/Raspberry/lib/e-Paper/EPD_IT8951.h"

#include <stdint.h>
#include <math.h>
#include <unistd.h>
#include <stdio.h>

int main(int argc, char *argv[])
{
    int exit_status = 0;
    int opt = 0;
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
        exit_status = 3;

        fprintf(
            stderr,
            "%s\n",
            "Connected device is not a 10.3 inch e-paper device.");
    }

    target_memory_address = device_info.Memory_Addr_L | (device_info.Memory_Addr_H << 16);

    if (file_path != NULL)
    {
        if (str_ends_with(file_path, ".bmp") == 0)
        {
            if (display_bmp_image(device_info, target_memory_address, file_path) != 0)
            {
                exit_status = 4;

                fprintf(
                    stderr,
                    "%s (%s).\n",
                    "Error during drawing BMP image onto display",
                    file_path);

                EPD_IT8951_Clear_Refresh(device_info, target_memory_address, INIT_Mode);
            }
        }
        else if (str_ends_with(file_path, ".4bpp") == 0)
        {
            if (display_4bpp_image(device_info, target_memory_address, file_path) != 0)
            {
                exit_status = 4;

                fprintf(
                    stderr,
                    "%s (%s).\n",
                    "Error during drawing 4bpp image onto display",
                    file_path);

                EPD_IT8951_Clear_Refresh(device_info, target_memory_address, INIT_Mode);
            }
        }
        else
        {
            exit_status = 5;

            fprintf(
                stderr,
                "%s\n",
                "Unsupported image file format.");
        }
    }
    else
    {
        EPD_IT8951_Clear_Refresh(device_info, target_memory_address, INIT_Mode);
    }

    EPD_IT8951_Sleep();
    DEV_Module_Exit();

    return exit_status;
}
