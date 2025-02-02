#!/bin/bash
# prepare options list from directory search
unset locations i
while IFS= read -r -d $'\0' directory; do
  prefix="./group_vars/location_"
  location=${directory/#$prefix}
  locations[i++]="$location"
done < <(find ./group_vars/ -maxdepth 1 -type d -name "location_*" -print0 | sort -z)

# show menu
echo "Usage:

This helper script allows you to perform bbb-config related tasks via an easy menu.
Either select a location by typing the corresponding number or one of the following
actions by just typing them.

Actions:
  abort
    return to the command line
  all
    generage images for all nodes and locations and return to the command line
  clean
    delete all temporary files generated by bbb-configs and wait for additional
    commands
  lint
    check all configuration files by calling yamllint and ansible-lint and
    return to the command line
  requirements
    install the requirements and wait for additional commands
" >&2

echo "The following locations were found:
" >&2
PS3="
Use a location number to generate images for that location or type an action: "

# allow the user to choose a location
unset location
select location in "${locations[@]}"
  do
    # abort if selected
    if [[ "$REPLY" == abort ]]; then break; fi

    # generate all images if selected
    if [[ "$REPLY" == all ]] 
    then
        ansible-playbook play.yml --tags image && echo "location of generated images: /tmp/ansible-openwrt/images"
        break
    fi

    # delete old directories and get rid of artifacts
    if [[ "$REPLY" == clean ]]
    then
        [ -d "/tmp/ansible-openwrt/" ] && rm -r /tmp/ansible-openwrt/
        echo "tmp directory was deleted..."
        continue
    fi

    # check all configurations files with ansible-lint
    if [[ "$REPLY" == lint ]]
    then
        yamllint -d .github/linters/.yaml-lint.yml .
        ansible-lint -c .github/linters/.ansible-lint.yml
        break
    fi

    # install or update requirements
    if [[ "$REPLY" == requirements ]]
    then
        pip3 install -r requirements.txt
        continue
    fi

    # complain if no location was selected, and loop to ask again
    if [[ "$location" == "" ]]
    then
        echo "'$REPLY' is not a valid selection"
        continue
    fi

    # generate images
    echo "firmwares for the following location will be generated:"
    echo "$location"
    ansible-playbook play.yml --limit "location_$location" --tags image && echo "location of generated images: /tmp/ansible-openwrt/images"

    # break the loop
    break
  done
