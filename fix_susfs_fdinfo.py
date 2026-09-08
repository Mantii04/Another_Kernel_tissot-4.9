filepath = 'fs/notify/fdinfo.c'
try:
    with open(filepath, 'r') as f:
        content = f.read()
    
    old_code = "\tif (inode) {\n\t\t/*\n\t\t * IN_ALL_EVENTS represents all of the mask bits"
    new_code = "\tif (inode) {\n#ifdef CONFIG_KSU_SUSFS_SUS_MOUNT\n\t\tu32 mask = mark->mask & IN_ALL_EVENTS;\n\t\tif (likely(current->susfs_task_state & TASK_STRUCT_NON_ROOT_USER_APP_PROC) &&\n\t\t\t\tunlikely(inode->i_state & INODE_STATE_SUS_KSTAT)) {\n\t\t\tstruct path path;\n\t\t\tchar *pathname = kmalloc(PAGE_SIZE, GFP_KERNEL);\n\t\t\tchar *dpath;\n\t\t\tif (!pathname) {\n\t\t\t\tgoto out_seq_printf;\n\t\t\t}\n\t\t\tdpath = d_path(&file->f_path, pathname, PAGE_SIZE);\n\t\t\tif (!dpath) {\n\t\t\t\tgoto out_free_pathname;\n\t\t\t}\n\t\t\tif (kern_path(dpath, 0, &path)) {\n\t\t\t\tgoto out_free_pathname;\n\t\t\t}\n\t\t\tseq_printf(m, \"inotify wd:%x ino:%lx sdev:%x mask:%x ignored_mask:%x \",\n\t\t\t   inode_mark->wd, path.dentry->d_inode->i_ino, path.dentry->d_inode->i_sb->s_dev,\n\t\t\t   mask, mark->ignored_mask);\n\t\t\tshow_mark_fhandle(m, path.dentry->d_inode);\n\t\t\tseq_putc(m, '\\n');\n\t\t\tiput(inode);\n\t\t\tpath_put(&path);\n\t\t\tkfree(pathname);\n\t\t\treturn;\nout_free_pathname:\n\t\t\tkfree(pathname);\n\t\t}\nout_seq_printf:\n#endif\n\t\t/*\n\t\t * IN_ALL_EVENTS represents all of the mask bits"
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        # Also comment out the original u32 mask line below
        content = content.replace("\t\tu32 mask = mark->mask & IN_ALL_EVENTS;", "\t\t//u32 mask = mark->mask & IN_ALL_EVENTS;")
        with open(filepath, 'w') as f:
            f.write(content)
        print("Manually patched fdinfo.c 4th hunk!")
    else:
        print("Could not find context for fdinfo.c 4th hunk!")

except Exception as e:
    print(f"Error: {e}")
