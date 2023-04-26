#!/bin/bash

set -euf -o pipefail

script_dir="$(dirname "$(realpath "$0")")"

target_config_dir='/etc/slow-movie-player'
target_main_dir='/opt/slow-movie-player'

service_name='slow-movie-player.service'

declare -a directories=(
    # path:user:group:permissions
    "${target_config_dir}:root:root:0755"
    "${target_main_dir}:root:root:0700"
)

declare -a files=(
    # source_path:target_path:user:group:permissions
    "${script_dir}/build/update-display:${target_main_dir}/update-display:root:root:0700"
    "${script_dir}/fixups/default.conf:${target_config_dir}/default.conf:root:root:0644"
    "${script_dir}/fixups/${service_name}:/etc/systemd/system/${service_name}:root:root:0644"
    "${script_dir}/src/slow-movie-player-service/configuration.py:${target_main_dir}/configuration.py:root:root:0600"
    "${script_dir}/src/slow-movie-player-service/display.py:${target_main_dir}/display.py:root:root:0600"
    "${script_dir}/src/slow-movie-player-service/grayscalemethod.py:${target_main_dir}/grayscalemethod.py:root:root:0600"
    "${script_dir}/src/slow-movie-player-service/image.py:${target_main_dir}/image.py:root:root:0600"
    "${script_dir}/src/slow-movie-player-service/processinfo.py:${target_main_dir}/processinfo.py:root:root:0600"
    "${script_dir}/src/slow-movie-player-service/skip.py:${target_main_dir}/skip.py:root:root:0600"
    "${script_dir}/src/slow-movie-player-service/slowmovieplayer.py:${target_main_dir}/slowmovieplayer.py:root:root:0700"
    "${script_dir}/src/slow-movie-player-service/video.py:${target_main_dir}/video.py:root:root:0600"
    "${script_dir}/src/slow-movie-player-service/videolibrary.py:${target_main_dir}/videolibrary.py:root:root:0600"
)

declare -a pycache_directories=()

# Check if array contains item [$1: item, $2: array name]
in_array()
{
    local needle="$1"
    local -n haystack="$2"

    for element in "${haystack[@]}"
    do
        [[ "${element}" == "${needle}" ]] && return 0
    done

    return 1
}

create_directories()
{
    for directory_properties in "${directories[@]}"
    do
        IFS=':' read -r dir_path dir_user dir_group dir_permissions <<< "${directory_properties}"

        mkdir "${dir_path}"
        chown "${dir_user}:${dir_group}" "${dir_path}"
        chmod "${dir_permissions}" "${dir_path}"
    done
}

copy_files()
{
    for file_properties in "${files[@]}"
    do
        IFS=':' read -r source_path target_path file_user file_group file_permissions <<< "${file_properties}"

        cp "${source_path}" "${target_path}"
        chown "${file_user}:${file_group}" "${target_path}"
        chmod "${file_permissions}" "${target_path}"
    done
}

remove_files()
{
    for file_properties in "${files[@]}"
    do
        IFS=':' read -r _ target_path _ <<< "${file_properties}"

        rm -f "${target_path}"

        if [[ "${target_path: -3}" == '.py' ]]
        then
            directory_path="${target_path%/*}"
            file_name_wo_extension="${target_path##*/}"
            file_name_wo_extension="${file_name_wo_extension%.*}"
            pycache_directory="${directory_path}/__pycache__"
            pycache_file_pattern="${pycache_directory}/${file_name_wo_extension}."

            (
                set +f

                rm -f "${pycache_file_pattern}"*'.pyc'

                set -f
            )

            if [[ -d "${pycache_directory}" ]] && ! in_array "${pycache_directory}" pycache_directories
            then
                pycache_directories+=("${pycache_directory}")
            fi
        fi
    done
}

remove_directories()
{
    for pycache_directory in "${pycache_directories[@]}"
    do
        rmdir "${pycache_directory}"
    done

    for directory_properties in "${directories[@]}"
    do
        IFS=':' read -r dir_path _ <<< "${directory_properties}"

        rmdir "${dir_path}"
    done
}

enable_service()
{
    if ! systemctl is-enabled --quiet "${service_name}"
    then
        systemctl enable "${service_name}"
    fi
}

stop_service()
{
    if systemctl is-active --quiet "${service_name}"
    then
        systemctl stop "${service_name}"
    fi
}

disable_service()
{
    if systemctl is-enabled --quiet "${service_name}"
    then
        systemctl disable "${service_name}"
    fi
}

install_slow_movie_player()
{
    create_directories
    copy_files
    enable_service
}

uninstall_slow_movie_player()
{
    stop_service
    disable_service
    remove_files
    remove_directories
}

show_usage()
{
    printf '%s\n'                                             \
        'Usage: ./setup.sh -h | -i | -u'                      \
        'Install or uninstall the Slow Movie Player Service.' \
        ''                                                    \
        'Options:'                                            \
        '  -h  Print this help.'                              \
        '  -i  Install the Slow Movie Player Service.'        \
        '  -u  Uninstall the Slow Movie Player Service.'      \
        ''                                                    \
        'Please note that you must specify exactly one option at a time.'
}

if (($# != 1)) || [[ "$1" != '-'* ]]
then
    printf '%s\n' 'No or invalid (number of) option(s) specified.' >&2

    show_usage

    exit 1
fi

while getopts 'hiu' option
do
    case "${option}"
    in
        'h')
            show_usage
            ;;
        'i')
            install_slow_movie_player
            ;;
        'u')
            uninstall_slow_movie_player
            ;;
        \?)
            show_usage
            exit 1
    esac
done
