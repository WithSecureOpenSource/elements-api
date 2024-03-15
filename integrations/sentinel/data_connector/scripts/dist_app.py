import os
import zipfile
from pathlib import Path

PROJECT_ROOT_DIR = "data_connector"
ZIP_RELATIVE_PATH = "target/app.zip"
RESULT_DEPENDENCIES_PATH = ".python_packages/lib/site-packages"
EXCLUDE_FOLDERS = (".venv/bin", "scripts", "tests")
INCLUDE_EXTENSIONS = (".py", ".properties")
INCLUDE_FILES = ("host.json", "function.json")


def dist_app():
    """Function creates zip file under ZIP_RELATIVE_PATH. It traverses paths from the root folder of the project.
    Folders from EXCLUDE_FOLDERS are skipped, files that match extensions from INCLUDE_EXTENSIONS or match names from
    INCLUDE_FILES are added to the zip in their relative paths from the root folder of the project. Dependency files
    from .venv site-packages folder are added regardless of their extension or name. Relative paths of those are
    mapped to RESULT_DEPENDENCIES_PATH in the zip file. Final zip has the format that is understood by the Azure
    Functions.
    """
    print("Start packaging zip...")
    print(f"Output path is {ZIP_RELATIVE_PATH}")

    script_name = str(__file__).split("/")[-1]
    scripts_dir = Path(os.path.dirname(__file__))
    project_root = scripts_dir.parent
    if project_root.name != PROJECT_ROOT_DIR:
        raise Exception(
            f"Invalid path of the {script_name} script. Script depends on detecting project root directory."
        )

    target_path = os.path.join(project_root, ZIP_RELATIVE_PATH)
    target_dir = os.path.dirname(target_path)

    if not Path(target_dir).exists():
        os.mkdir(os.path.relpath(target_dir, project_root))
    with zipfile.ZipFile(target_path, "w", zipfile.ZIP_DEFLATED) as archive:
        _write_files(os.path.join(project_root, "app"), archive)
        _write_files(os.path.join(project_root, ".venv"), archive)
    print("Finished packaging zip")


def _write_files(project_root, result_file):
    for root, dirs, files in os.walk(project_root):
        if _is_skip_path(root):
            continue
        for file_name in files:
            if _is_included(root, file_name):
                _write_file(result_file, project_root, root, file_name)


def _is_skip_path(path):
    for exclude_folder in EXCLUDE_FOLDERS:
        if exclude_folder in path:
            return True
    return False


def _is_included(path, file_name):
    if _is_in_dependencies(path):
        return True
    elif file_name.startswith("test_"):
        return False
    elif file_name in INCLUDE_FILES:
        return True
    for include_extension in INCLUDE_EXTENSIONS:
        if file_name.endswith(include_extension):
            return True
    return False


def _is_in_dependencies(path):
    return ".venv" in path and "site-packages" in path


def _write_file(result_file, project_root, path, file_name):
    file_path = os.path.join(path, file_name)
    relative_path = os.path.relpath(file_path, project_root)
    result_path = relative_path
    if ".venv" in path and "site-packages" in path:
        site_packages_rel_path = relative_path.split("site-packages/")[1]
        result_path = os.path.join(RESULT_DEPENDENCIES_PATH, site_packages_rel_path)

    result_file.write(file_path, result_path)
