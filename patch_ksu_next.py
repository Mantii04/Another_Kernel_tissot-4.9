import sys

def patch_file(filepath, old_str, new_str):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        if old_str in content:
            content = content.replace(old_str, new_str)
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Patched {filepath}")
        else:
            print(f"Could not find context in {filepath}")
    except Exception as e:
        print(f"Error patching {filepath}: {e}")

# fs/exec.c
patch_file('fs/exec.c',
    'int do_execve(struct filename *filename,',
    '#ifdef CONFIG_KSU\n__attribute__((hot))\nextern int ksu_handle_execveat(int *fd, struct filename **filename_ptr,\n\t\t\t       void *argv, void *envp, int *flags);\n#endif\n\nint do_execve(struct filename *filename,')

patch_file('fs/exec.c',
    '\treturn do_execveat_common(AT_FDCWD, filename, argv, envp, 0);\n}',
    '\t#ifdef CONFIG_KSU\n\tksu_handle_execveat((int *)AT_FDCWD, &filename, &argv, &envp, 0);\n\t#endif\n\n\treturn do_execveat_common(AT_FDCWD, filename, argv, envp, 0);\n}')

# fs/open.c
patch_file('fs/open.c',
    'SYSCALL_DEFINE3(faccessat, int, dfd, const char __user *, filename, int, mode)',
    '#ifdef CONFIG_KSU\n__attribute__((hot))\nextern int ksu_handle_faccessat(int *dfd, const char __user **filename_user,\n\t\t\t        int *mode, int *flags);\n#endif\n\nSYSCALL_DEFINE3(faccessat, int, dfd, const char __user *, filename, int, mode)')

patch_file('fs/open.c',
    '\tif (mode & ~S_IRWXO)\n\t\treturn -EINVAL;',
    '\t#ifdef CONFIG_KSU\n\tksu_handle_faccessat(&dfd, &filename, &mode, NULL);\n\t#endif\n\n\tif (mode & ~S_IRWXO)\n\t\treturn -EINVAL;')

# fs/read_write.c - FIXED TARGETING
patch_file('fs/read_write.c',
    'SYSCALL_DEFINE3(read, unsigned int, fd, char __user *, buf, size_t, count)\n{\n\tstruct fd f = fdget_pos(fd);\n\tssize_t ret = -EBADF;\n\n\tif (f.file) {',
    '#ifdef CONFIG_KSU\nextern bool ksu_vfs_read_hook __read_mostly;\nextern __attribute__((cold)) int ksu_handle_sys_read(unsigned int fd,\n\t\t\t\t\t\t       char __user **buf_ptr, size_t *count_ptr);\n#endif\n\nSYSCALL_DEFINE3(read, unsigned int, fd, char __user *, buf, size_t, count)\n{\n\tstruct fd f = fdget_pos(fd);\n\tssize_t ret = -EBADF;\n\n\t#ifdef CONFIG_KSU\n\tif (unlikely(ksu_vfs_read_hook))\n\t\tksu_handle_sys_read(fd, &buf, &count);\n\t#endif\n\n\tif (f.file) {')

# fs/stat.c
patch_file('fs/stat.c',
    'int vfs_fstatat(int dfd, const char __user *filename, struct kstat *stat,',
    '#ifdef CONFIG_KSU\n__attribute__((hot))\nextern int ksu_handle_stat(int *dfd, const char __user **filename_user,\n\t\t\t   int *flags);\n#endif\n\nint vfs_fstatat(int dfd, const char __user *filename, struct kstat *stat,')

patch_file('fs/stat.c',
    '\tif ((flag & ~(AT_SYMLINK_NOFOLLOW | AT_NO_AUTOMOUNT |',
    '\t#ifdef CONFIG_KSU \n\tksu_handle_stat(&dfd, &filename, &flag);\n\t#endif\n\n\tif ((flag & ~(AT_SYMLINK_NOFOLLOW | AT_NO_AUTOMOUNT |')

# kernel/reboot.c
patch_file('kernel/reboot.c',
    'SYSCALL_DEFINE4(reboot, int, magic1, int, magic2, unsigned int, cmd, void __user *, arg)',
    '#ifdef CONFIG_KSU\nextern int ksu_handle_sys_reboot(int magic1, int magic2, unsigned int cmd, void __user **arg);\n#endif\n\nSYSCALL_DEFINE4(reboot, int, magic1, int, magic2, unsigned int, cmd, void __user *, arg)')

patch_file('kernel/reboot.c',
    '\tif (!ns_capable(pid_ns->user_ns, CAP_SYS_BOOT))\n\t\treturn -EPERM;',
    '\t#ifdef CONFIG_KSU\n\tksu_handle_sys_reboot(magic1, magic2, cmd, &arg);\n\t#endif\n\n\tif (!ns_capable(pid_ns->user_ns, CAP_SYS_BOOT))\n\t\treturn -EPERM;')
