#include "test.h"

int main(void)
{
    test_str_ends_with_without_mocks();
    test_str_ends_with_with_null_parameters();
    test_str_ends_with_with_substring_longer_than_string();
    test_str_ends_with_when_strings_differ();

    test_print_help();

    test_display_bmp_image();
    test_display_bmp_image_with_null_file_path();
    test_display_bmp_image_when_image_buffer_allocation_fails();
    test_display_bmp_image_when_gui_read_bmp_fails();

    test_display_4bpp_image();
    test_display_4bpp_image_with_null_file_path();
    test_display_4bpp_image_with_stat_call_failing();
    test_display_4bpp_image_with_too_small_image_size();
    test_display_4bpp_image_with_no_image_data_in_file();
    test_display_4bpp_image_when_file_open_fails();
    test_display_4bpp_image_when_fread_returns_incorrect_number_of_items_read();
    test_display_4bpp_image_with_too_high_image_resolution();
    test_display_4bpp_image_using_image_with_odd_number_of_total_pixels();
    test_display_4bpp_image_with_wrong_file_size_and_resolutions();
    test_display_4bpp_image_when_malloc_fails();
    test_display_4bpp_image_when_reading_image_data_fails();

    return 0;
}
