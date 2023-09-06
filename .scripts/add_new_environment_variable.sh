#!/bin/bash

handle_error() {
  local error_line="${BASH_LINENO[0]}"
  local error_command="${BASH_COMMAND}"
  echo "Error: An error occurred on line $error_line. Command: '$error_command'"
}

trap 'handle_error' ERR

append_to_env() {
  [ ! -f "./.env" ] && echo "Error: .env not found" && exit 1
  echo "${1^^}=\"${2^^}\"" >> .env
}

append_to_env_template() {
  [ ! -f ".env.template" ] && echo "Error: .env.template not found" && exit 1
  echo "${1^^}=\"${2^^}\"" >> .env.template
}

append_to_configurations_py() {
  configurations_file="./src/configs/configurations.py"
  [ ! -f "${configurations_file}" ] && echo "Error: ${configurations_file} not found" && exit 1 
  echo "" > s
  echo "    def get_${1,,}():" >> ${configurations_file}
  echo "        return Configurations._get_variable_value(\"${1^^}\")" >> ${configurations_file}
  echo "" >> ${configurations_file}
}

while getopts "k:v:" opt; do
  case $opt in
    k) key="$OPTARG" ;;
    v) value="$OPTARG" ;;
    \?) echo "Invalid option: -$OPTARG" >&2; exit 1 ;;
  esac
done

if [ -z "$key" ] || [ -z "$value" ]; then
  echo "Usage: $0 -k KEY -v VALUE (both are mandatory)"
  exit 1
fi

append_to_env "$key" "$value"

append_to_env_template "$key" "$value"

append_to_configurations_py "$key" "$value"

echo "Environment variable added to .env, .env.template and configurations.py."
