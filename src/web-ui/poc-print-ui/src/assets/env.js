(function (window) {
  window["env"] = window["env"] || {};

  window["env"]["isProduction"] = false;
  window["env"]["apiUrl"] = "http://localhost:8000/api";
  window["env"]["tenantIdHeader"] = "Pph-Tenant-Id";
  window["env"]["tenantTokenHeader"] = "Pph-Tenant-Token";
})(this);