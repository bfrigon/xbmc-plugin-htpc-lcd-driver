#!/bin/sh




ADDON_XML=`find . -name addon.xml |  head -n 1`

if [ ! -f "${ADDON_XML}" ]
then
        echo "No addon.xml was found in this project tree"
        exit 1
fi


ADDON_ID=`sed -ne 's/<addon.*id="\([^"]*\).*/\1/p' ${ADDON_XML}`
if [ -z ${ADDON_ID} ]
then
    echo "Could not find addon id in addon.xml!"
    exit 1
fi

ADDON_VERSION=`sed -ne 's/<addon.*version="\([^"]*\).*/\1/p' ${ADDON_XML}`
if [ -z ${ADDON_VERSION} ]
then
    echo "Could not find addon version in addon.xml!"
    exit 1
fi


echo "Addon ID : ${ADDON_ID}"
echo "Version  : ${ADDON_VERSION}"
echo

if [ ! -d ${ADDON_ID} ]
then
    echo "The addon files needs to be in a subdirectory with the same name as the addon id"
    exit 1
fi



OUTPUT="${ADDON_ID}-${ADDON_VERSION}.zip"

echo "Creating ZIP archive... (${OUTPUT})"

rm -f ${OUTPUT}
zip ${OUTPUT} ${ADDON_ID} -rq

echo "Done!"

