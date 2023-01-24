CC = gcc
# TODO: Add -Werror to WARN_O
WARN_O = -Wall -Wpedantic -Wextra
STD = -std=gnu99
CFLAGS = $(STD) -O3 $(WARN_O)
D_CFLAGS = $(STD) -DDEBUG -g -O0 $(WARN_O)
LFLAGS = -lbcm2835 -lm -lrt -lpthread

LIB_DIR = ../../vendor/IT8951-ePaper/Raspberry/lib
BUILD_DIR = ../../build

OBJS = ${BUILD_DIR}/main.o           \
       ${BUILD_DIR}/update_display.o \
       ${BUILD_DIR}/DEV_Config.o     \
       ${BUILD_DIR}/EPD_IT8951.o     \
       ${BUILD_DIR}/GUI_BMPfile.o    \
       ${BUILD_DIR}/GUI_Paint.o

TARGET = update-display

.PHONY: all clean debug

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o ${BUILD_DIR}/$@ $(LFLAGS)

${BUILD_DIR}/main.o: main.c
	$(CC) $(CFLAGS) -c $< -o $@ $(LFLAGS)

${BUILD_DIR}/update_display.o: update_display.c
	$(CC) $(CFLAGS) -c $< -o $@ $(LFLAGS)

$(BUILD_DIR)/DEV_Config.o: $(LIB_DIR)/Config/DEV_Config.c
	$(CC) $(CFLAGS) -c $< -o $@ $(LFLAGS)

${BUILD_DIR}/EPD_IT8951.o: $(LIB_DIR)/e-Paper/EPD_IT8951.c
	$(CC) $(CFLAGS) -c $< -o $@ $(LFLAGS)

${BUILD_DIR}/GUI_BMPfile.o: $(LIB_DIR)/GUI/GUI_BMPfile.c
	$(CC) $(CFLAGS) -c $< -o $@ $(LFLAGS)

${BUILD_DIR}/GUI_Paint.o: $(LIB_DIR)/GUI/GUI_Paint.c
	$(CC) $(CFLAGS) -c $< -o $@ $(LFLAGS)

clean:
	rm -fv $(BUILD_DIR)/$(TARGET) $(OBJS)

debug: CFLAGS = $(D_CFLAGS)
debug: all
