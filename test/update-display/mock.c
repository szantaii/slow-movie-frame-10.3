#include "mock.h"
#include <assert.h>

#define UNUSED(arg) (void)(arg)

#define ABORT()                                                                                                \
    fprintf(stdout, "%s:%d: %s: Mock is not initialized for (further) use!\n", __FILE__, __LINE__, __func__ ); \
    fprintf(stderr, "%s:%d: %s: Mock is not initialized for (further) use!\n", __FILE__, __LINE__, __func__ ); \
    fflush(NULL);                                                                                              \
    assert(!"Mock is not initialized for (further) use!");

uint8_t INIT_Mode = 0;

// fclose
size_t fclose_mock_call_count = 0;

// fopen
size_t fopen_mock_return_value_count = 0;
size_t fopen_mock_call_count = 0;
uint8_t *fopen_mock_return_values = NULL;

// fread
size_t fread_mock_return_value_count = 0;
size_t fread_mock_call_count = 0;
fread_mock_read_value_type_t *fread_mock_read_value_types = NULL;
size_t *fread_mock_return_values = NULL;
uint16_t *fread_mock_read_values = NULL;

// free
size_t free_mock_call_count = 0;

// malloc
size_t malloc_mock_return_value_count = 0;
size_t malloc_mock_call_count = 0;
uint8_t *malloc_mock_return_values = NULL;

// stat
size_t stat_mock_return_value_count = 0;
size_t stat_mock_call_count = 0;
int *stat_mock_return_values = NULL;
off_t *stat_mock_st_size_values = NULL;

// strcmp
size_t strcmp_mock_return_value_count = 0;
size_t strcmp_mock_call_count = 0;
int *strcmp_mock_return_values = NULL;

// strlen
size_t strlen_mock_return_value_count = 0;
size_t strlen_mock_call_count = 0;
size_t *strlen_mock_return_values = NULL;

// EPD_IT8951_4bp_Refresh
size_t epd_it8951_4bp_refresh_mock_call_count = 0;

// EPD_IT8951_8bp_Refresh
size_t epd_it8951_8bp_refresh_mock_call_count = 0;

// EPD_IT8951_Clear_Refresh
size_t epd_it8951_clear_refresh_mock_call_count = 0;

// GUI_ReadBmp
size_t gui_read_bmp_return_value_count = 0;
size_t gui_read_bmp_call_count = 0;
uint8_t *gui_read_bmp_return_values = NULL;

void reset_fclose_mock(void)
{
    fclose_mock_call_count = 0;
}

void reset_fopen_mock(void)
{
    if (NULL != fopen_mock_return_values)
    {
        __real_free(fopen_mock_return_values);
        fopen_mock_return_values = NULL;
    }

    fopen_mock_return_value_count = 0;
    fopen_mock_call_count = 0;
}

void reset_fread_mock(void)
{
    if (NULL != fread_mock_return_values)
    {
        __real_free(fread_mock_return_values);
        fread_mock_return_values = NULL;
    }

    if (NULL != fread_mock_read_value_types)
    {
        __real_free(fread_mock_read_value_types);
        fread_mock_read_value_types = NULL;
    }

    if (NULL != fread_mock_read_values)
    {
        __real_free(fread_mock_read_values);
        fread_mock_read_values = NULL;
    }

    fread_mock_return_value_count = 0;
    fread_mock_call_count = 0;
}

void reset_free_mock(void)
{
    free_mock_call_count = 0;
}

void reset_malloc_mock(void)
{
    if (NULL != malloc_mock_return_values)
    {
        __real_free(malloc_mock_return_values);
        malloc_mock_return_values = NULL;
    }

    malloc_mock_return_value_count = 0;
    malloc_mock_call_count = 0;
}

void reset_stat_mock(void)
{
    if (NULL != stat_mock_return_values)
    {
        __real_free(stat_mock_return_values);
        stat_mock_return_values = NULL;
    }

    if (NULL != stat_mock_st_size_values)
    {
        __real_free(stat_mock_st_size_values);
        stat_mock_st_size_values = NULL;
    }

    stat_mock_return_value_count = 0;
    stat_mock_call_count = 0;
}

void reset_strcmp_mock(void)
{
    if (NULL != strcmp_mock_return_values)
    {
        __real_free(strcmp_mock_return_values);
        strcmp_mock_return_values = NULL;
    }

    strcmp_mock_return_value_count = 0;
    strcmp_mock_call_count = 0;
}

void reset_strlen_mock(void)
{
    if (NULL != strlen_mock_return_values)
    {
        __real_free(strlen_mock_return_values);
        strlen_mock_return_values = NULL;
    }

    strlen_mock_return_value_count = 0;
    strlen_mock_call_count = 0;
}

void reset_epd_it8951_4bp_refresh_mock(void)
{
    epd_it8951_4bp_refresh_mock_call_count = 0;
}

void reset_epd_it8951_8bp_refresh_mock(void)
{
    epd_it8951_8bp_refresh_mock_call_count = 0;
}

void reset_epd_it8951_clear_refresh_mock(void)
{
    epd_it8951_clear_refresh_mock_call_count = 0;
}

void reset_gui_read_bmp_mock(void)
{
    if (NULL != gui_read_bmp_return_values)
    {
        __real_free(gui_read_bmp_return_values);
        gui_read_bmp_return_values = NULL;
    }

    gui_read_bmp_return_value_count = 0;
    gui_read_bmp_call_count = 0;
}

void reset_mocks(void)
{
    reset_fclose_mock();
    reset_fopen_mock();
    reset_fread_mock();
    reset_free_mock();
    reset_malloc_mock();
    reset_stat_mock();
    reset_strcmp_mock();
    reset_strlen_mock();
    reset_epd_it8951_4bp_refresh_mock();
    reset_epd_it8951_8bp_refresh_mock();
    reset_epd_it8951_clear_refresh_mock();
    reset_gui_read_bmp_mock();
}

int __wrap_fclose(FILE *stream)
{
    UNUSED(stream);

    ++fclose_mock_call_count;

    return 0;
}

FILE *__wrap_fopen(const char *path, const char *mode)
{
    UNUSED(path);
    UNUSED(mode);

    if (NULL != fopen_mock_return_values
        && fopen_mock_call_count < fopen_mock_return_value_count)
    {
        return (FILE *)(uintptr_t)fopen_mock_return_values[fopen_mock_call_count++];
    }

    ABORT();
}

size_t __wrap_fread(void *ptr, size_t size, size_t count, FILE *stream)
{
    UNUSED(size);
    UNUSED(count);
    UNUSED(stream);

    if (NULL != fread_mock_return_values
        && NULL != fread_mock_read_value_types
        && NULL != fread_mock_read_values
        && fread_mock_call_count < fread_mock_return_value_count)
    {
        switch (fread_mock_read_value_types[fread_mock_call_count])
        {
        case UINT8_T_TYPE:
            ptr = (void *)(uintptr_t)fread_mock_read_values[fread_mock_call_count];
            break;

        case UINT16_T_TYPE:
            *(uint16_t *)ptr = fread_mock_read_values[fread_mock_call_count];
            break;

        default:
            ABORT();
            break;
        }

        return fread_mock_return_values[fread_mock_call_count++];
    }

    ABORT();
}

void __wrap_free(void *ptr)
{
    UNUSED(ptr);

    ++free_mock_call_count;

    return;
}

void *__wrap_malloc(size_t size)
{
    UNUSED(size);

    if (NULL != malloc_mock_return_values
        && malloc_mock_call_count < malloc_mock_return_value_count)
    {
        return (void *)(uintptr_t)malloc_mock_return_values[malloc_mock_call_count++];
    }

    ABORT();
}

int __wrap___xstat(int ver, const char *path, struct stat *stat_buf)
{
    UNUSED(ver);
    UNUSED(path);

    if (NULL != stat_mock_return_values
        && NULL != stat_mock_st_size_values
        && stat_mock_call_count < stat_mock_return_value_count)
    {
        stat_buf->st_size = stat_mock_st_size_values[stat_mock_call_count];

        return stat_mock_return_values[stat_mock_call_count++];
    }

    ABORT();
}

int __wrap_strcmp(const char *str1, const char *str2)
{
    if (NULL == strcmp_mock_return_values
        && 0 == strcmp_mock_return_value_count)
    {
        return __real_strcmp(str1, str2);
    }

    if (NULL != strcmp_mock_return_values
        && strcmp_mock_call_count < strcmp_mock_return_value_count)
    {
        return strcmp_mock_return_values[strcmp_mock_call_count++];
    }

    ABORT();
}

size_t __wrap_strlen(const char *str)
{
    if (NULL == strlen_mock_return_values
        && 0 == strlen_mock_return_value_count)
    {
        return __real_strlen(str);
    }

    if (NULL != strlen_mock_return_values
        && strlen_mock_call_count < strlen_mock_return_value_count)
    {
        return strlen_mock_return_values[strlen_mock_call_count++];
    }

    ABORT();
}

void __wrap_EPD_IT8951_4bp_Refresh(
    uint8_t *frame_buffer,
    uint16_t x,
    uint16_t y,
    uint16_t width,
    uint16_t height,
    bool hold,
    uint32_t target_memory_address,
    bool packed_write)
{
    UNUSED(frame_buffer);
    UNUSED(x);
    UNUSED(y);
    UNUSED(width);
    UNUSED(height);
    UNUSED(hold);
    UNUSED(target_memory_address);
    UNUSED(packed_write);

    ++epd_it8951_4bp_refresh_mock_call_count;

    return;
}

void __wrap_EPD_IT8951_8bp_Refresh(
    uint8_t *frame_buffer,
    uint16_t x,
    uint16_t y,
    uint16_t width,
    uint16_t height,
    bool hold,
    uint32_t target_memory_address)
{
    UNUSED(frame_buffer);
    UNUSED(x);
    UNUSED(y);
    UNUSED(width);
    UNUSED(height);
    UNUSED(hold);
    UNUSED(target_memory_address);

    ++epd_it8951_8bp_refresh_mock_call_count;

    return;
}

void __wrap_EPD_IT8951_Clear_Refresh(
    IT8951_Dev_Info device_info,
    uint32_t target_memory_address,
    uint16_t mode)
{
    UNUSED(device_info);
    UNUSED(target_memory_address);
    UNUSED(mode);

    ++epd_it8951_clear_refresh_mock_call_count;

    return;
}

uint8_t __wrap_GUI_ReadBmp(const char *path, uint16_t x, uint16_t y)
{
    UNUSED(path);
    UNUSED(x);
    UNUSED(y);

    if (NULL != gui_read_bmp_return_values
        && gui_read_bmp_call_count < gui_read_bmp_return_value_count)
    {
        return gui_read_bmp_return_values[gui_read_bmp_call_count++];
    }

    ABORT();
}

void __wrap_Paint_Clear(uint16_t color)
{
    UNUSED(color);

    return;
}

void __wrap_Paint_NewImage(
    uint8_t *image,
    uint16_t width,
    uint16_t height,
    uint16_t rotate,
    uint16_t color)
{
    UNUSED(image);
    UNUSED(width);
    UNUSED(height);
    UNUSED(rotate);
    UNUSED(color);

    return;
}

void __wrap_Paint_SelectImage(uint8_t *image)
{
    UNUSED(image);

    return;
}

void __wrap_Paint_SetBitsPerPixel(uint8_t bits_per_pixel)
{
    UNUSED(bits_per_pixel);

    return;
}

void __wrap_Paint_SetMirroring(uint8_t mirror)
{
    UNUSED(mirror);

    return;
}

void __wrap_Paint_SetRotate(uint16_t rotate)
{
    UNUSED(rotate);

    return;
}
