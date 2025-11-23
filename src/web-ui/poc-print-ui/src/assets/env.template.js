(function (window) {
  window["env"] = window["env"] || {};

  window["env"]["isProduction"] = "${ENV_PROD}";
  window["env"]["apiUrl"] = "${ENV_API_URL}";
})(this);
