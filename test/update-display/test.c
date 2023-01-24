#define _GNU_SOURCE
#include "../../src/update-display/update_display.h"
#include "mock.h"

#include <assert.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

#define COMMA ,

#define TEST_CASE(name, stdout_str, stderr_str, body)                    \
void name(void)                                                          \
{                                                                        \
    int stdout_pipe_fd[2] = {-1, -1};                                    \
    int stdout_backup = -1;                                              \
    int stderr_pipe_fd[2] = {-1, -1};                                    \
    int stderr_backup = -1;                                              \
                                                                         \
    fprintf(stdout, "%s ... ", __func__);                                \
    fflush(NULL);                                                        \
                                                                         \
    if (NULL != stdout_str)                                              \
    {                                                                    \
        stdout_backup = dup(fileno(stdout));                             \
                                                                         \
        pipe2(stdout_pipe_fd, O_NONBLOCK);                               \
                                                                         \
        fflush(stdout);                                                  \
                                                                         \
        dup2(stdout_pipe_fd[1], fileno(stdout));                         \
    }                                                                    \
                                                                         \
    if (NULL != stderr_str)                                              \
    {                                                                    \
        stderr_backup = dup(fileno(stderr));                             \
                                                                         \
        pipe2(stderr_pipe_fd, O_NONBLOCK);                               \
                                                                         \
        fflush(stderr);                                                  \
                                                                         \
        dup2(stderr_pipe_fd[1], fileno(stderr));                         \
    }                                                                    \
                                                                         \
    reset_mocks();                                                       \
                                                                         \
    body                                                                 \
                                                                         \
    if (NULL != stdout_str                                               \
        || NULL != stderr_str)                                           \
    {                                                                    \
        fflush(NULL);                                                    \
    }                                                                    \
                                                                         \
    reset_mocks();                                                       \
                                                                         \
    if (NULL != stdout_str)                                              \
    {                                                                    \
        close(stdout_pipe_fd[1]);                                        \
        dup2(stdout_backup, fileno(stdout));                             \
                                                                         \
        int stdout_buffer_size = fcntl(stdout_pipe_fd[0], F_GETPIPE_SZ); \
        ++stdout_buffer_size;                                            \
                                                                         \
        char stdout_buf[stdout_buffer_size];                             \
        memset(stdout_buf, '\0', stdout_buffer_size * sizeof(char));     \
                                                                         \
        read(stdout_pipe_fd[0], stdout_buf, stdout_buffer_size);         \
                                                                         \
        assert(0 == __real_strcmp(stdout_str, stdout_buf));              \
    }                                                                    \
                                                                         \
    if (NULL != stderr_str)                                              \
    {                                                                    \
        close(stderr_pipe_fd[1]);                                        \
        dup2(stderr_backup, fileno(stderr));                             \
                                                                         \
        int stderr_buffer_size = fcntl(stderr_pipe_fd[0], F_GETPIPE_SZ); \
        ++stderr_buffer_size;                                            \
                                                                         \
        char stderr_buf[stderr_buffer_size];                             \
        memset(stderr_buf, '\0', stderr_buffer_size * sizeof(char));     \
                                                                         \
        read(stderr_pipe_fd[0], stderr_buf, stderr_buffer_size);         \
                                                                         \
        assert(0 == __real_strcmp(stderr_str, stderr_buf));              \
    }                                                                    \
                                                                         \
    fprintf(stdout, "ok\n");                                             \
}

// fclose
extern size_t fclose_mock_call_count;

// fopen
extern size_t fopen_mock_return_value_count;
extern size_t fopen_mock_call_count;
extern uint8_t *fopen_mock_return_values;

// fread
extern size_t fread_mock_return_value_count;
extern size_t fread_mock_call_count;
extern size_t *fread_mock_return_values;
extern fread_mock_read_value_type_t *fread_mock_read_value_types;
extern uint16_t *fread_mock_read_values;

// free
extern size_t free_mock_call_count;

// malloc
extern size_t malloc_mock_return_value_count;
extern size_t malloc_mock_call_count;
extern uint8_t *malloc_mock_return_values;

// stat
extern size_t stat_mock_return_value_count;
extern size_t stat_mock_call_count;
extern int *stat_mock_return_values;
extern off_t *stat_mock_st_size_values;

// strcmp
extern size_t strcmp_mock_return_value_count;
extern size_t strcmp_mock_call_count;
extern int *strcmp_mock_return_values;

// strlen
extern size_t strlen_mock_return_value_count;
extern size_t strlen_mock_call_count;
extern size_t *strlen_mock_return_values;

// EPD_IT8951_4bp_Refresh
extern size_t epd_it8951_4bp_refresh_mock_call_count;

// EPD_IT8951_8bp_Refresh
extern size_t epd_it8951_8bp_refresh_mock_call_count;

// EPD_IT8951_Clear_Refresh
extern size_t epd_it8951_clear_refresh_mock_call_count;

// GUI_ReadBmp
extern size_t gui_read_bmp_return_value_count;
extern size_t gui_read_bmp_call_count;
extern uint8_t *gui_read_bmp_return_values;

TEST_CASE(
    test_str_ends_with_without_mocks,
    NULL,
    NULL,

    assert(0 == strlen_mock_call_count);
    assert(0 == strcmp_mock_call_count);

    assert(-1 == str_ends_with(NULL, NULL));
    assert(-1 == str_ends_with(NULL, "abc"));
    assert(-1 == str_ends_with("abc", NULL));

    assert(1 == str_ends_with("sato", "rotas"));
    assert(1 == str_ends_with("sator", "rotas"));

    assert(0 == str_ends_with("abc", "abc"));
    assert(0 == str_ends_with("abc", "bc"));
    assert(0 == str_ends_with("abc", "c"));
    assert(0 == str_ends_with("abc", ""));
    assert(0 == str_ends_with("", ""));

    assert(0 == strlen_mock_call_count);
    assert(0 == strcmp_mock_call_count);
)

TEST_CASE(
    test_str_ends_with_with_null_parameters,
    NULL,
    NULL,

    strlen_mock_return_value_count = 6;
    strlen_mock_return_values = calloc(strlen_mock_return_value_count, sizeof(size_t));
    strlen_mock_return_values[0] = 1;
    strlen_mock_return_values[1] = 1;
    strlen_mock_return_values[2] = 1;
    strlen_mock_return_values[3] = 1;
    strlen_mock_return_values[4] = 1;
    strlen_mock_return_values[5] = 1;

    strcmp_mock_return_value_count = 3;
    strcmp_mock_return_values = calloc(strcmp_mock_return_value_count, sizeof(int));
    strcmp_mock_return_values[0] = 0;
    strcmp_mock_return_values[1] = 0;
    strcmp_mock_return_values[2] = 0;

    assert(0 == strlen_mock_call_count);
    assert(0 == strcmp_mock_call_count);

    assert(-1 == str_ends_with(NULL, NULL));
    assert(-1 == str_ends_with(NULL, "abc"));
    assert(-1 == str_ends_with("abc", NULL));

    assert(0 == strlen_mock_call_count);
    assert(0 == strcmp_mock_call_count);
)

TEST_CASE(
    test_str_ends_with_with_substring_longer_than_string,
    NULL,
    NULL,

    strlen_mock_return_value_count = 2;
    strlen_mock_return_values = calloc(strlen_mock_return_value_count, sizeof(size_t));
    strlen_mock_return_values[0] = 1;
    strlen_mock_return_values[1] = 2;

    assert(1 == str_ends_with("does", "not matter"));
)

TEST_CASE(
    test_str_ends_with_when_strings_differ,
    NULL,
    NULL,

    strlen_mock_return_value_count = 4;
    strlen_mock_return_values = calloc(strlen_mock_return_value_count, sizeof(size_t));
    strlen_mock_return_values[0] = 2;
    strlen_mock_return_values[1] = 2;
    strlen_mock_return_values[2] = 3;
    strlen_mock_return_values[3] = 2;

    strcmp_mock_return_value_count = 2;
    strcmp_mock_return_values = calloc(strcmp_mock_return_value_count, sizeof(int));
    strcmp_mock_return_values[0] = 1;
    strcmp_mock_return_values[1] = 1;

    assert(1 == str_ends_with("rotas", "rotas"));
    assert(1 == str_ends_with("tenet", "net"));
)

TEST_CASE(
    test_print_help,
    "Usage: update-display -v VOLTAGE [-f <IMAGE_FILE> | -h]\n"
    "Update the display of the connected 10.3 e-paper device either\n"
    "by clearing it or drawing a 8bit per channel RGB BMP or a custom\n"
    "4bits per pixel image on it.\n"
    "\n"
    "Mandatory option:\n"
    "  -v VOLTAGE  use the VOLTAGE for the connected e-paper device\n"
    "              (Read and use the exact voltage from the flexible\n"
    "              printed circuit cable of the connected device.)\n"
    "\n"
    "Optional options:\n"
    "  -f IMAGE_FILE  draw the specified image on the display of the\n"
    "                 connected e-paper device\n"
    "  -h             display this help and exit\n"
    "\n"
    "Exit status:\n"
    "  0  success\n"
    "  1  wrong command-line arguments or command-line parsing error\n"
    "  2  failed to initialize bcm2835 device\n"
    "  3  the connected device is not a 10.3 inch e-paper device\n"
    "  4  error during drawing BMP/4BPP image onto display\n"
    "  5  unsupported image file format\n"
    "\n"
    "Examples:\n"
    "  ./update-display -h\n"
    "  ./update-display -v -2.51\n"
    "  ./update-display -v -1.50 -f /path/to/image.bmp\n"
    "  ./update-display -v -1.48 -f /path/to/image.4bpp\n"
    "\n",
    NULL,

    print_help();
)

TEST_CASE(
    test_display_bmp_image,
    NULL,
    NULL,

    IT8951_Dev_Info device_info;

    malloc_mock_return_value_count = 1;
    malloc_mock_return_values = calloc(malloc_mock_return_value_count, sizeof(uint8_t));
    malloc_mock_return_values[0] = 1;

    gui_read_bmp_return_value_count = 1;
    gui_read_bmp_return_values = calloc(gui_read_bmp_return_value_count, sizeof(uint8_t));

    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);
    assert(0 == epd_it8951_clear_refresh_mock_call_count);
    assert(0 == epd_it8951_8bp_refresh_mock_call_count);

    assert(0 == display_bmp_image(device_info, 0, "/dummy/file/path"));

    assert(1 == malloc_mock_call_count);
    assert(1 == free_mock_call_count);
    assert(1 == epd_it8951_clear_refresh_mock_call_count);
    assert(1 == epd_it8951_8bp_refresh_mock_call_count);
)

TEST_CASE(
    test_display_bmp_image_with_null_file_path,
    NULL,
    "Received null pointer for file path.\n",

    IT8951_Dev_Info device_info;

    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-1 == display_bmp_image(device_info, 0, NULL));

    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);
)

TEST_CASE(
    test_display_bmp_image_when_image_buffer_allocation_fails,
    NULL,
    "Cannot allocate enough memory for image buffer (2628288 bytes).\n",

    IT8951_Dev_Info device_info = {
        1872 COMMA
        1404 COMMA
        0 COMMA
        0 COMMA
        {0 COMMA 0 COMMA 0 COMMA 0 COMMA 0 COMMA 0 COMMA 0 COMMA 0} COMMA
        {0 COMMA 0 COMMA 0 COMMA 0 COMMA 0 COMMA 0 COMMA 0 COMMA 0}
    };

    malloc_mock_return_value_count = 1;
    malloc_mock_return_values = calloc(malloc_mock_return_value_count, sizeof(uint8_t));

    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-2 == display_bmp_image(device_info, 0, "/dummy/file/path"));

    assert(1 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);
)

TEST_CASE(
    test_display_bmp_image_when_gui_read_bmp_fails,
    NULL,
    "Cannot process BMP image or allocate enough memory.\n",

    IT8951_Dev_Info device_info;

    malloc_mock_return_value_count = 1;
    malloc_mock_return_values = calloc(malloc_mock_return_value_count, sizeof(uint8_t));
    malloc_mock_return_values[0] = 1;

    gui_read_bmp_return_value_count = 1;
    gui_read_bmp_return_values = calloc(gui_read_bmp_return_value_count, sizeof(uint8_t));
    gui_read_bmp_return_values[0] = 1;

    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-3 == display_bmp_image(device_info, 0, "/dummy/file/path"));

    assert(1 == malloc_mock_call_count);
    assert(1 == free_mock_call_count);
)

TEST_CASE(
    test_display_4bpp_image,
    NULL,
    NULL,

    IT8951_Dev_Info device_info;

    stat_mock_return_value_count = 1;
    stat_mock_return_values = calloc(stat_mock_return_value_count, sizeof(int));
    stat_mock_st_size_values = calloc(stat_mock_return_value_count, sizeof(off_t));
    stat_mock_st_size_values[0] = 2 * sizeof(uint16_t) + (1872 * 1404) / 2;

    fopen_mock_return_value_count = 1;
    fopen_mock_return_values = calloc(fopen_mock_return_value_count, sizeof(uint8_t));
    fopen_mock_return_values[0] = 1;

    fread_mock_return_value_count = 3;
    fread_mock_return_values = calloc(fread_mock_return_value_count, sizeof(size_t));
    fread_mock_read_value_types = calloc(fread_mock_return_value_count, sizeof(fread_mock_read_value_type_t));
    fread_mock_read_values = calloc(fread_mock_return_value_count, sizeof(uint16_t));
    fread_mock_return_values[0] = 1;
    fread_mock_return_values[1] = 1;
    fread_mock_return_values[2] = 1;
    fread_mock_read_value_types[0] = UINT16_T_TYPE;
    fread_mock_read_value_types[1] = UINT16_T_TYPE;
    fread_mock_read_value_types[2] = UINT8_T_TYPE;
    fread_mock_read_values[0] = 1872;
    fread_mock_read_values[1] = 1404;
    fread_mock_read_values[2] = 1;

    malloc_mock_return_value_count = 1;
    malloc_mock_return_values = calloc(malloc_mock_return_value_count, sizeof(uint8_t));
    malloc_mock_return_values[0] = 1;

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);
    assert(0 == epd_it8951_clear_refresh_mock_call_count);
    assert(0 == epd_it8951_4bp_refresh_mock_call_count);

    assert(0 == display_4bpp_image(device_info, 0, "/dummy/file/path"));

    assert(1 == fclose_mock_call_count);
    assert(1 == malloc_mock_call_count);
    assert(1 == free_mock_call_count);
    assert(1 == epd_it8951_clear_refresh_mock_call_count);
    assert(1 == epd_it8951_4bp_refresh_mock_call_count);
)

TEST_CASE(
    test_display_4bpp_image_with_null_file_path,
    NULL,
    "Received null pointer for file path.\n",

    IT8951_Dev_Info device_info;

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-1 == display_4bpp_image(device_info, 0, NULL));

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);
)

TEST_CASE(
    test_display_4bpp_image_with_stat_call_failing,
    NULL,
    "Unable to get file status (/dummy/file/path).\n",

    IT8951_Dev_Info device_info;

    stat_mock_return_value_count = 1;
    stat_mock_return_values = calloc(stat_mock_return_value_count, sizeof(int));
    stat_mock_st_size_values = calloc(stat_mock_return_value_count, sizeof(off_t));
    stat_mock_return_values[0] = 1;
    stat_mock_st_size_values[0] = 1;

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-2 == display_4bpp_image(device_info, 0, "/dummy/file/path"));

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);
)

TEST_CASE(
    test_display_4bpp_image_with_too_small_image_size,
    NULL,
    "File size is smaller than the minimum size of a 4bpp image (/dummy/file/path).\n",

    IT8951_Dev_Info device_info;

    stat_mock_return_value_count = 1;
    stat_mock_return_values = calloc(stat_mock_return_value_count, sizeof(int));
    stat_mock_st_size_values = calloc(stat_mock_return_value_count, sizeof(off_t));
    stat_mock_st_size_values[0] = 2 * sizeof(uint16_t) - 1;

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-3 == display_4bpp_image(device_info, 0, "/dummy/file/path"));

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);
)

TEST_CASE(
    test_display_4bpp_image_with_no_image_data_in_file,
    NULL,
    "No image data in file, not drawing anything to display (/dummy/file/path).\n",

    IT8951_Dev_Info device_info;

    stat_mock_return_value_count = 1;
    stat_mock_return_values = calloc(stat_mock_return_value_count, sizeof(int));
    stat_mock_st_size_values = calloc(stat_mock_return_value_count, sizeof(off_t));
    stat_mock_st_size_values[0] = 2 * sizeof(uint16_t);

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);
    assert(0 == epd_it8951_clear_refresh_mock_call_count);

    assert(0 == display_4bpp_image(device_info, 0, "/dummy/file/path"));

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);
    assert(1 == epd_it8951_clear_refresh_mock_call_count);
)

TEST_CASE(
    test_display_4bpp_image_when_file_open_fails,
    NULL,
    "Cannot open file (/dummy/file/path).\n",

    IT8951_Dev_Info device_info;

    stat_mock_return_value_count = 1;
    stat_mock_return_values = calloc(stat_mock_return_value_count, sizeof(int));
    stat_mock_st_size_values = calloc(stat_mock_return_value_count, sizeof(off_t));
    stat_mock_st_size_values[0] = 2 * sizeof(uint16_t) + 1;

    fopen_mock_return_value_count = 1;
    fopen_mock_return_values = calloc(fopen_mock_return_value_count, sizeof(uint8_t));

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-4 == display_4bpp_image(device_info, 0, "/dummy/file/path"));

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);
)

TEST_CASE(
    test_display_4bpp_image_when_fread_returns_incorrect_number_of_items_read,
    NULL,
    "Invalid 4bpp image file (/dummy/file/path/1).\n"
    "Invalid 4bpp image file (/dummy/file/path/2).\n",

    IT8951_Dev_Info device_info;

    stat_mock_return_value_count = 2;
    stat_mock_return_values = calloc(stat_mock_return_value_count, sizeof(int));
    stat_mock_st_size_values = calloc(stat_mock_return_value_count, sizeof(off_t));
    stat_mock_st_size_values[0] = 2 * sizeof(uint16_t) + 1;
    stat_mock_st_size_values[1] = stat_mock_st_size_values[0];

    fopen_mock_return_value_count = 2;
    fopen_mock_return_values = calloc(fopen_mock_return_value_count, sizeof(uint8_t));
    fopen_mock_return_values[0] = 1;
    fopen_mock_return_values[1] = fopen_mock_return_values[0];

    fread_mock_return_value_count = 3;
    fread_mock_return_values = calloc(fread_mock_return_value_count, sizeof(size_t));
    fread_mock_read_value_types = calloc(fread_mock_return_value_count, sizeof(fread_mock_read_value_type_t));
    fread_mock_read_values = calloc(fread_mock_return_value_count, sizeof(uint16_t));
    fread_mock_return_values[0] = 0;
    fread_mock_return_values[1] = 1;
    fread_mock_return_values[2] = 2;
    fread_mock_read_value_types[0] = UINT16_T_TYPE;
    fread_mock_read_value_types[1] = UINT16_T_TYPE;
    fread_mock_read_value_types[2] = UINT16_T_TYPE;
    fread_mock_read_values[0] = 0;
    fread_mock_read_values[1] = 0;
    fread_mock_read_values[2] = 0;

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-5 == display_4bpp_image(device_info, 0, "/dummy/file/path/1"));

    assert(1 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-5 == display_4bpp_image(device_info, 0, "/dummy/file/path/2"));

    assert(2 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);
)

TEST_CASE(
    test_display_4bpp_image_with_too_high_image_resolution,
    NULL,
    "Image resolution is higher than the maximum allowed (2^16 - 2 pixels by 2^16 - 1 pixels).\n",

    IT8951_Dev_Info device_info;

    stat_mock_return_value_count = 1;
    stat_mock_return_values = calloc(stat_mock_return_value_count, sizeof(int));
    stat_mock_st_size_values = calloc(stat_mock_return_value_count, sizeof(off_t));
    stat_mock_st_size_values[0] = 2 * sizeof(uint16_t) + 1;

    fopen_mock_return_value_count = 1;
    fopen_mock_return_values = calloc(fopen_mock_return_value_count, sizeof(uint8_t));
    fopen_mock_return_values[0] = 1;

    fread_mock_return_value_count = 2;
    fread_mock_return_values = calloc(fread_mock_return_value_count, sizeof(size_t));
    fread_mock_read_value_types = calloc(fread_mock_return_value_count, sizeof(fread_mock_read_value_type_t));
    fread_mock_read_values = calloc(fread_mock_return_value_count, sizeof(uint16_t));
    fread_mock_return_values[0] = 1;
    fread_mock_return_values[1] = 1;
    fread_mock_read_value_types[0] = UINT16_T_TYPE;
    fread_mock_read_value_types[1] = UINT16_T_TYPE;
    fread_mock_read_values[0] = 65535;
    fread_mock_read_values[1] = 65535;

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-6 == display_4bpp_image(device_info, 0, "/dummy/file/path"));

    assert(1 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);
)

TEST_CASE(
    test_display_4bpp_image_using_image_with_odd_number_of_total_pixels,
    NULL,
    "The number of pixels in this 4bpp image is odd! The number of pixels in a 4bpp image must be even.\n",

    IT8951_Dev_Info device_info;

    stat_mock_return_value_count = 1;
    stat_mock_return_values = calloc(stat_mock_return_value_count, sizeof(int));
    stat_mock_st_size_values = calloc(stat_mock_return_value_count, sizeof(off_t));
    stat_mock_st_size_values[0] = 2 * sizeof(uint16_t) + 1;

    fopen_mock_return_value_count = 1;
    fopen_mock_return_values = calloc(fopen_mock_return_value_count, sizeof(uint8_t));
    fopen_mock_return_values[0] = 1;

    fread_mock_return_value_count = 2;
    fread_mock_return_values = calloc(fread_mock_return_value_count, sizeof(size_t));
    fread_mock_read_value_types = calloc(fread_mock_return_value_count, sizeof(fread_mock_read_value_type_t));
    fread_mock_read_values = calloc(fread_mock_return_value_count, sizeof(uint16_t));
    fread_mock_return_values[0] = 1;
    fread_mock_return_values[1] = 1;
    fread_mock_read_value_types[0] = UINT16_T_TYPE;
    fread_mock_read_value_types[1] = UINT16_T_TYPE;
    fread_mock_read_values[0] = 3;
    fread_mock_read_values[1] = 3;

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-7 == display_4bpp_image(device_info, 0, "/dummy/file/path"));

    assert(1 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);
)

TEST_CASE(
    test_display_4bpp_image_with_wrong_file_size_and_resolutions,
    NULL,
    "Invalid 4bpp image file (/dummy/file/path/1).\n"
    "Invalid 4bpp image file (/dummy/file/path/2).\n"
    "Invalid 4bpp image file (/dummy/file/path/3).\n",

    IT8951_Dev_Info device_info;

    stat_mock_return_value_count = 3;
    stat_mock_return_values = calloc(stat_mock_return_value_count, sizeof(int));
    stat_mock_st_size_values = calloc(stat_mock_return_value_count, sizeof(off_t));
    stat_mock_st_size_values[0] = 2 * sizeof(uint16_t) + 1;
    stat_mock_st_size_values[1] = 2 * sizeof(uint16_t) + 1;
    stat_mock_st_size_values[2] = 2 * sizeof(uint16_t) + (1872 * 1404) / 2 + 1;

    fopen_mock_return_value_count = 3;
    fopen_mock_return_values = calloc(fopen_mock_return_value_count, sizeof(uint8_t));
    fopen_mock_return_values[0] = 1;
    fopen_mock_return_values[1] = 1;
    fopen_mock_return_values[2] = 1;

    fread_mock_return_value_count = 6;
    fread_mock_return_values = calloc(fread_mock_return_value_count, sizeof(size_t));
    fread_mock_read_value_types = calloc(fread_mock_return_value_count, sizeof(fread_mock_read_value_type_t));
    fread_mock_read_values = calloc(fread_mock_return_value_count, sizeof(uint16_t));
    fread_mock_return_values[0] = 1;
    fread_mock_return_values[1] = 1;
    fread_mock_return_values[2] = 1;
    fread_mock_return_values[3] = 1;
    fread_mock_return_values[4] = 1;
    fread_mock_return_values[5] = 1;
    fread_mock_read_value_types[0] = UINT16_T_TYPE;
    fread_mock_read_value_types[1] = UINT16_T_TYPE;
    fread_mock_read_value_types[2] = UINT16_T_TYPE;
    fread_mock_read_value_types[3] = UINT16_T_TYPE;
    fread_mock_read_value_types[4] = UINT16_T_TYPE;
    fread_mock_read_value_types[5] = UINT16_T_TYPE;
    fread_mock_read_values[0] = 0;
    fread_mock_read_values[1] = 1404;
    fread_mock_read_values[2] = 1872;
    fread_mock_read_values[3] = 0;
    fread_mock_read_values[4] = 1872;
    fread_mock_read_values[5] = 1404;

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-8 == display_4bpp_image(device_info, 0, "/dummy/file/path/1"));

    assert(1 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-8 == display_4bpp_image(device_info, 0, "/dummy/file/path/2"));

    assert(2 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-8 == display_4bpp_image(device_info, 0, "/dummy/file/path/3"));

    assert(3 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);
)

TEST_CASE(
    test_display_4bpp_image_when_malloc_fails,
    NULL,
    "Cannot allocate enough memory for 4bpp image data.\n",

    IT8951_Dev_Info device_info;

    stat_mock_return_value_count = 1;
    stat_mock_return_values = calloc(stat_mock_return_value_count, sizeof(int));
    stat_mock_st_size_values = calloc(stat_mock_return_value_count, sizeof(off_t));
    stat_mock_st_size_values[0] = 2 * sizeof(uint16_t) + (1872 * 1404) / 2;

    fopen_mock_return_value_count = 1;
    fopen_mock_return_values = calloc(fopen_mock_return_value_count, sizeof(uint8_t));
    fopen_mock_return_values[0] = 1;

    fread_mock_return_value_count = 2;
    fread_mock_return_values = calloc(fread_mock_return_value_count, sizeof(size_t));
    fread_mock_read_value_types = calloc(fread_mock_return_value_count, sizeof(fread_mock_read_value_type_t));
    fread_mock_read_values = calloc(fread_mock_return_value_count, sizeof(uint16_t));
    fread_mock_return_values[0] = 1;
    fread_mock_return_values[1] = 1;
    fread_mock_read_value_types[0] = UINT16_T_TYPE;
    fread_mock_read_value_types[1] = UINT16_T_TYPE;
    fread_mock_read_values[0] = 1872;
    fread_mock_read_values[1] = 1404;

    malloc_mock_return_value_count = 1;
    malloc_mock_return_values = calloc(malloc_mock_return_value_count, sizeof(uint8_t));

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-9 == display_4bpp_image(device_info, 0, "/dummy/file/path"));

    assert(1 == fclose_mock_call_count);
    assert(1 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);
)

TEST_CASE(
    test_display_4bpp_image_when_reading_image_data_fails,
    NULL,
    "Failed to read 4bpp image data.\n",

    IT8951_Dev_Info device_info;

    stat_mock_return_value_count = 1;
    stat_mock_return_values = calloc(stat_mock_return_value_count, sizeof(int));
    stat_mock_st_size_values = calloc(stat_mock_return_value_count, sizeof(off_t));
    stat_mock_st_size_values[0] = 2 * sizeof(uint16_t) + (1872 * 1404) / 2;

    fopen_mock_return_value_count = 1;
    fopen_mock_return_values = calloc(fopen_mock_return_value_count, sizeof(uint8_t));
    fopen_mock_return_values[0] = 1;

    fread_mock_return_value_count = 3;
    fread_mock_return_values = calloc(fread_mock_return_value_count, sizeof(size_t));
    fread_mock_read_value_types = calloc(fread_mock_return_value_count, sizeof(fread_mock_read_value_type_t));
    fread_mock_read_values = calloc(fread_mock_return_value_count, sizeof(uint16_t));
    fread_mock_return_values[0] = 1;
    fread_mock_return_values[1] = 1;
    fread_mock_read_value_types[0] = UINT16_T_TYPE;
    fread_mock_read_value_types[1] = UINT16_T_TYPE;
    fread_mock_read_value_types[2] = UINT8_T_TYPE;
    fread_mock_read_values[0] = 1872;
    fread_mock_read_values[1] = 1404;
    fread_mock_read_values[2] = 0;

    malloc_mock_return_value_count = 1;
    malloc_mock_return_values = calloc(malloc_mock_return_value_count, sizeof(uint8_t));
    malloc_mock_return_values[0] = 1;

    assert(0 == fclose_mock_call_count);
    assert(0 == malloc_mock_call_count);
    assert(0 == free_mock_call_count);

    assert(-10 == display_4bpp_image(device_info, 0, "/dummy/file/path"));

    assert(1 == fclose_mock_call_count);
    assert(1 == malloc_mock_call_count);
    assert(1 == free_mock_call_count);
)
