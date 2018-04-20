CC=g++
CC_FLAGS= -O3 -std=c++11 -Wall
SRCS:=$(shell find *.cc)
OBJS:= $(SRCS:%.cc=%.o)
INC_DIRS=-I../pybind11/include -I/System/Library/Frameworks/Python.framework/Headers
LIB_DIRS=-L/System/Library/Frameworks/Python.framework/
TARGET=libdda.so

all: $(TARGET)

full: clean all

%.o : %.cc %.h
	$(CC) $(CC_FLAGS) $(INC_DIRS) -c $<

$(TARGET): $(OBJS)
	$(CC) $(LIB_DIRS) -lPython -dynamiclib -o $(TARGET) $^

clean:
	rm -f *.o $(TARGET)
