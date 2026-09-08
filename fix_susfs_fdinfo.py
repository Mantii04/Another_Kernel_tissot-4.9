filepath = 'fs/notify/fdinfo.c'
try:
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Find the exact line: "inode = igrab(mark->inode);"
    # The 4th hunk adds the SuSFS block right after this line.
    found = False
    for i, line in enumerate(lines):
        if 'inode = igrab(mark->inode);' in line:
            # Check if the next line is "if (inode) {"
            if i + 1 < len(lines) and 'if (inode) {' in lines[i+1]:
                # Check if we already patched it
                if 'CONFIG_KSU_SUSFS_SUS_MOUNT' in lines[i+2]:
                    print("fdinfo.c already patched!")
                    found = True
                    break
                
                # Insert the SuSFS block after "if (inode) {"
                susfs_block = [
                    "#ifdef CONFIG_KSU_SUSFS_SUS_MOUNT\n",
                    "\t\tu32 mask = mark->mask & IN_ALL_EVENTS;\n",
                    "\t\tif (likely(current->susfs_task_state & TASK_STRUCT_NON_ROOT_USER_APP_PROC) &&\n",
                    "\t\t\t\tunlikely(inode->i_state & INODE_STATE_SUS_KSTAT)) {\n",
                    "\t\t\tstruct path path;\n",
                    "\t\t\tchar *pathname = kmalloc(PAGE_SIZE, GFP_KERNEL);\n",
                    "\t\t\tchar *dpath;\n",
                    "\t\t\tif (!pathname) {\n",
                    "\t\t\t\tgoto out_seq_printf;\n",
                    "\t\t\t}\n",
                    "\t\t\tdpath = d_path(&file->f_path, pathname, PAGE_SIZE);\n",
                    "\t\t\tif (!dpath) {\n",
                    "\t\t\t\tgoto out_free_pathname;\n",
                    "\t\t\t}\n",
                    "\t\t\tif (kern_path(dpath, 0, &path)) {\n",
                    "\t\t\t\tgoto out_free_pathname;\n",
                    "\t\t\t}\n",
                    "\t\t\tseq_printf(m, \"inotify wd:%x ino:%lx sdev:%x mask:%x ignored_mask:%x \",\n",
                    "\t\t\t   inode_mark->wd, path.dentry->d_inode->i_ino, path.dentry->d_inode->i_sb->s_dev,\n",
                    "\t\t\t   mask, mark->ignored_mask);\n",
                    "\t\t\tshow_mark_fhandle(m, path.dentry->d_inode);\n",
                    "\t\t\tseq_putc(m, '\\\\n');\n",
                    "\t\t\tiput(inode);\n",
                    "\t\t\tpath_put(&path);\n",
                    "\t\t\tkfree(pathname);\n",
                    "\t\t\treturn;\n",
                    "out_free_pathname:\n",
                    "\t\t\tkfree(pathname);\n",
                    "\t\t}\n",
                    "out_seq_printf:\n",
                    "#endif\n",
                ]
                
                # Insert after "if (inode) {"
                lines[i+2:i+2] = susfs_block
                
                # Also comment out the original u32 mask line if it exists below
                for j in range(i+2, min(i+40, len(lines))):
                    if 'u32 mask = mark->mask & IN_ALL_EVENTS;' in lines[j]:
                        lines[j] = lines[j].replace('u32 mask', '//u32 mask')
                        break
                
                with open(filepath, 'w') as f:
                    f.writelines(lines)
                print("Manually patched fdinfo.c 4th hunk!")
                found = True
                break
    
    if not found:
        print("Could not find context for fdinfo.c 4th hunk!")

except Exception as e:
    print(f"Error: {e}")
