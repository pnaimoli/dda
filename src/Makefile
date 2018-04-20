CC=g++
CC_FLAGS= -O3 -std=c++11 -Wall -Wshadow -Werror
SRCS:=$(shell find *.cc)
OBJS:= $(SRCS:%.cc=%.o)
INC_DIRS=-isystem../pybind11/include
TARGET=libdda.so

all: $(TARGET)

full: clean all

%.o : %.cc %.h
	$(CC) $(CC_FLAGS) $(shell python3-config --include) $(INC_DIRS) -c $<

$(TARGET): $(OBJS)
	$(CC) $(shell python3-config --ldflags) -dynamiclib -o $(TARGET) $^

clean:
	rm -f *.o $(TARGET)
