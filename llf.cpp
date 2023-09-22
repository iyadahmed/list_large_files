#include <filesystem>
#include <iostream>
#include <vector>

#include "bytesize/bytesize.hh"

int main(int argc, char *argv[])
{
  const char *directory;
  if (argc == 1) {
    directory = ".";
  }
  else if (argc == 2) {
    directory = argv[1];
  }
  else {
    std::cerr << "Too many arguments." << std::endl;
    std::cerr << "Usage: llf [directory]" << std::endl;
    std::cerr << "If directory is not specified, the current directory is used." << std::endl;
    return 1;
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
  std::cout << std::filesystem::canonical(largest_file_path) << " "
            << bytesize::bytesize(largest_file_size) << std::endl;
  return 0;
}
