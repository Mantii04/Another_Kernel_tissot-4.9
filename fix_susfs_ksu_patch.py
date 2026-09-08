import urllib.request

url = "https://gitlab.com/simonpunk/susfs4ksu/-/raw/kernel-4.9/kernel_patches/KernelSU/10_enable_susfs_for_ksu.patch"
print("Downloading official 10_enable_susfs_for_ksu.patch...")
urllib.request.urlretrieve(url, "10_enable_susfs_for_ksu.patch")

print("Renaming old function names to match KernelSU-Next...")

with open("10_enable_susfs_for_ksu.patch", "r") as f:
    content = f.read()

# Map of old function names -> new KernelSU-Next names
renames = [
    ("is_manager_apk", "ksu_is_manager_apk"),
    ("is_manager()", "ksu_is_manager()"),
    ("escape_to_root", "ksu_escape_to_root"),
    ("on_post_fs_data", "ksu_on_post_fs_data"),
    ("apply_kernelsu_rules", "ksu_apply_kernelsu_rules"),
    ("setup_selinux", "ksu_setup_selinux"),
    ("setenforce", "ksu_setenforce"),
    ("getenforce", "ksu_getenforce"),
    ("is_ksu_domain", "ksu_is_ksu_domain"),
    ("is_zygote", "ksu_is_zygote"),
    ("track_throne", "ksu_track_throne"),
    ("handle_sepolicy", "ksu_handle_sepolicy"),
    ("kernelsu_init", "ksu_kernelsu_init"),
    ("kernelsu_exit", "ksu_kernelsu_exit"),
    ("try_umount", "ksu_try_umount"),
    ("persistent_allow_list", "ksu_persistent_allow_list"),
    ("do_save_allow_list", "ksu_do_save_allow_list"),
    ("do_load_allow_list", "ksu_do_load_allow_list"),
    ("should_umount", "ksu_should_umount"),
]

for old, new in renames:
    content = content.replace(old, new)
    print(f"  Renamed: {old} -> {new}")

with open("10_enable_susfs_for_ksu.patch", "w") as f:
    f.write(content)

print("Done! Patch file is ready.")
