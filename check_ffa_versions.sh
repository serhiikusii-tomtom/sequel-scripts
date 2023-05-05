#!/bin/bash
set -e

show_help()
{
   echo "Print FFA dependencies. It will checkout specified tag in hcp3-sdk-android."
   echo
   echo "Usage: check_ffa_versions.sh [OPTION]..."
   echo "options:"
   echo "v     FFA version. For example, 2023.5.1-dev."
   echo "f     Full info. Allow to checkout nk2-android tag"
   echo "h     Print this Help."
   echo
}

checkout_tag()
{
  tag_name=$1
  branch_name="branch_$tag_name"
  if [ -n "$(git branch --list $branch_name)" ]
  then
   echo "Checkout branch $branch_name in $PWD"
   git checkout $branch_name
   return
  fi

  echo "Checkout a new branch $branch_name in $PWD"
  git fetch --all --tags
  git checkout tags/$tag_name -b $branch_name
}

# Main program                                             

FFA_VERSION=$1
FULL_INFO=false
D_HSP3_SDK="hcp3-sdk-android"
D_ANDROID="nk2-android"
BRANCH_PREFIX="branch"

# Get the options
while getopts ":hv:f" option; do
   case $option in
      h|\?) 
         show_help
         exit 0
         ;;
      v) FFA_VERSION=$OPTARG
         ;;
      f) FULL_INFO=true
         ;;
   esac
done

if [ -z "${FFA_VERSION}" ]
then
  echo "Error: FFA version is not specified."
  show_help
  exit 1;
fi

cd $D_HSP3_SDK
checkout_tag $FFA_VERSION

android_version=$(grep "hcp3BomVersion" gradle.properties)
android_version=$(echo $android_version| cut -d'=' -f 2)
android_version=$(echo ${android_version//[[:blank:]]/})
echo "nk2-android version $android_version"
cd - > /dev/null

if [ "$FULL_INFO" = true ] ; then
    cd $D_ANDROID
    checkout_tag $android_version
    echo
    echo "nk2-android dependencies:"
    grep "nk2-" cxx-enablers/conanfile.ttlock
    cd - > /dev/null
fi
