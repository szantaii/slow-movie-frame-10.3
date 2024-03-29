void test_str_ends_with_without_mocks(void);
void test_str_ends_with_with_null_parameters(void);
void test_str_ends_with_with_substring_longer_than_string(void);
void test_str_ends_with_when_strings_differ(void);

void test_print_help(void);

void test_display_bmp_image(void);
void test_display_bmp_image_with_null_file_path(void);
void test_display_bmp_image_when_image_buffer_allocation_fails(void);
void test_display_bmp_image_when_gui_read_bmp_fails(void);

void test_display_4bpp_image(void);
void test_display_4bpp_image_with_null_file_path(void);
void test_display_4bpp_image_with_stat_call_failing(void);
void test_display_4bpp_image_with_too_small_image_size(void);
void test_display_4bpp_image_with_no_image_data_in_file(void);
void test_display_4bpp_image_when_file_open_fails(void);
void test_display_4bpp_image_when_fread_returns_incorrect_number_of_items_read(void);
void test_display_4bpp_image_with_too_high_image_resolution(void);
void test_display_4bpp_image_using_image_with_odd_number_of_total_pixels(void);
void test_display_4bpp_image_with_wrong_file_size_and_resolutions(void);
void test_display_4bpp_image_when_malloc_fails(void);
void test_display_4bpp_image_when_reading_image_data_fails(void);
