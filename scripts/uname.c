#include <stdio.h>
#include <unistd.h>
#include <sys/utsname.h>

int main() {
    struct utsname buf;
    uname(&buf);
    printf("%s\n", buf.machine);
    return 0;
}
