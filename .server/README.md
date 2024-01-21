
# Server/ Client comminication - Login

* Server send `<LOGIN> PublicKey`
* Server expects:
  * `<LOGIN_TOKEN> abc`
    * Good: `<LOGIN_TOKEN_SUCCESS>`
    * Fail: `<LOGIN_TOKEN_FAIL>`
    * Max: 1 Try (After: Ignore)
  * `<LOGIN> abc<SPLIT>abc`
    * Good: `<LOGIN_SUCCESS> TOKEN`
    * Fail: `<LOGIN_FAIL>`
    * Max: 3 Tries (After: `<LOGIN_CANCEL>`)
    * Note: Everything after "\<LOGIN\> " needs to be encrypted using the PublicKey.
  * `<LOGIN_NEW><User>abc</User><Password>abc</Password>`
    * Good: `<LOGIN_NEW_SUCCES>`
    * Fail: `<LOGIN_NEW_FAIL>`
    * Max: 1 Creation (After: Ignore)
    * Note: Password content needs to be encrypted using the PublicKey.
  * Anything else will be ignored.

# Server/ Client comminication

* After login process the server awaits any command.
  * `<MainCom> [Arguments]`
  * Eq: `Access`
  * Eq: `AM Read /File.json`
* Server processed command and returns one of the following:
  * " "
  * Json dump
  * String
  * `<CLOSE>`
