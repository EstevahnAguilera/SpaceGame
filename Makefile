CC = gcc
CFLAGS = -fPIC -shared
LDFLAGS = -lpthread

all: libgame_os.so

libgame_os.so: game_os.o
	$(CC) $(CFLAGS) -o $@ $^ $(LDFLAGS)

game_os.o: game_os.c game_os.h
	$(CC) -c -fPIC $< -o $@

clean:
	rm -f *.o *.so 