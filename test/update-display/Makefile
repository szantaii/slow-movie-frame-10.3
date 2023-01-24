CC = gcc
WARN_O = -Werror -Wall -Wpedantic -Wextra
STD = -std=gnu99
CFLAGS = $(STD) -O3 $(WARN_O)
D_CFLAGS = $(STD) -DDEBUG -g -O0 $(WARN_O)
LFLAGS = -lbcm2835 -lm -lrt -lpthread
M_LFLAGS = -Wl,--wrap=fclose                   \
           -Wl,--wrap=fopen                    \
           -Wl,--wrap=fread                    \
           -Wl,--wrap=free                     \
           -Wl,--wrap=malloc                   \
           -Wl,--wrap=__xstat                  \
           -Wl,--wrap=strcmp                   \
           -Wl,--wrap=strlen                   \
           -Wl,--wrap=EPD_IT8951_4bp_Refresh   \
           -Wl,--wrap=EPD_IT8951_8bp_Refresh   \
           -Wl,--wrap=EPD_IT8951_Clear_Refresh \
           -Wl,--wrap=GUI_ReadBmp              \
           -Wl,--wrap=Paint_Clear              \
           -Wl,--wrap=Paint_NewImage           \
           -Wl,--wrap=Paint_SelectImage        \
           -Wl,--wrap=Paint_SetBitsPerPixel    \
           -Wl,--wrap=Paint_SetMirroring       \
           -Wl,--wrap=Paint_SetRotate

SRC_DIR = ../../src/update-display
BUILD_DIR = ../../build

OBJS = ${BUILD_DIR}/test_main.o           \
       ${BUILD_DIR}/test_test.o           \
       ${BUILD_DIR}/test_update_display.o \
       ${BUILD_DIR}/test_mock.o

TARGET = test-update-display

.PHONY: all clean debug

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o ${BUILD_DIR}/$@ $(LFLAGS) $(M_LFLAGS)

${BUILD_DIR}/test_main.o: main.c
	$(CC) $(CFLAGS) -c $< -o $@ $(LFLAGS)

${BUILD_DIR}/test_test.o: test.c
	$(CC) $(CFLAGS) -c $< -o $@ $(LFLAGS)

${BUILD_DIR}/test_update_display.o: $(SRC_DIR)/update_display.c
	$(CC) $(CFLAGS) -c $< -o $@ $(LFLAGS)

${BUILD_DIR}/test_mock.o: mock.c
	$(CC) $(CFLAGS) -c $< -o $@ $(LFLAGS)

clean:
	rm -fv $(BUILD_DIR)/$(TARGET) $(OBJS)

debug: CFLAGS = $(D_CFLAGS)
debug: all
