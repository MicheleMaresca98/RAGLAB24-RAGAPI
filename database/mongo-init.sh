#!/usr/bin/env bash
set -eu
mongo -- "$MONGO_INITDB_DATABASE" <<EOF
    var rootUser = '$MONGO_INITDB_ROOT_USERNAME';
    var rootPassword = '$MONGO_INITDB_ROOT_PASSWORD';
    var admin = db.getSiblingDB('admin');
    admin.auth(rootUser, rootPassword);

   use aaa
   db.createCollection("users")
   db.users.insertOne({
      "firstName":"Michele",
      "lastName":"Maresca",
      "taxIdentificationNumber":"MRSMHL98T14C129J",
      "role":"administrator",
      "mobilePhone": "+393317060581",
      "organization":{
         "path":"bit4id-test",
         "level":1,
         "leaf":true
      },
      "permissions":[
      ],
      "authentication":[
         {
            "mechanism": "basic",
            "credentials": {
               "username": "test",
               "password": "baaf00c8f6d2afc84e2d9c01dd5c11e7150fc7b467e0de139ef7729e04dcfaa0"
            }
         },
         {
            "mechanism": "apikey",
            "credentials": {
               "key":"89db558c7266669fdacd4349601201e5458aeb2bbb5727bb56a29fadf2e9c418"
            }
         }
      ]
   })
EOF


