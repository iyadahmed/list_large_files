#include <filesystem>
#include <iostream>
#include <vector>

int main(int argc, char *argv[])
{
  const char *directory;
  if (argc == 1) {
    directory = ".";
  }
  else {
    directory = argv[1];
  }

  std::filesystem::path largest_file_path;
  std::uintmax_t largest_file_size = 0;

  for (const auto &entry : std::filesystem::recursive_directory_iterator(
           directory, std::filesystem::directory_options::skip_permission_denied))
  {
    if (!entry.is_regular_file())
      continue;
    const auto file_size = entry.file_size();
    if (file_size > largest_file_size) {
      largest_file_size = file_size;
      largest_file_path = entry.path();
    }
  }

  std::cout << largest_file_path.stem() << " " << largest_file_size << std::endl;
}
