(function (window) {
  window["env"] = window["env"] || {};

  window["env"]["isProduction"] = "${ENV_PROD}";
  window["env"]["apiUrl"] = "${ENV_API_URL}";
  window["env"]["tenantIdHeader"] = "${ENV_TENANT_ID_HEADER}";
  window["env"]["tenantTokenHeader"] = "${ENV_TENANT_TOKEN_HEADER}";
  window["env"]["messageOriginName"] = "${ENV_MESSAGE_ORIGIN_NAME}";
})(this);
