const BundleTracker = require("webpack-bundle-tracker");

const PUBLIC_PATH = process.env.PUBLIC_PATH || "http://127.0.0.1:8080/";

module.exports = {
    publicPath: PUBLIC_PATH,
    outputDir: "dist",
    assetsDir: "static",

    chainWebpack: config => {
        config
            .plugin('BundleTracker')
            .use(BundleTracker, [{filename: 'frontend/webpack-stats.json'}]);

        config.resolve.alias
            .set('__STATIC__', 'static');

        config.devServer
            .public('http://127.0.0.1:8080')
            .host('127.0.0.1')
            .port(8080)
            .hotOnly(true)
            .watchOptions({poll: 1000})
            .https(false)
            .headers({"Access-Control-Allow-Origin": ["\\*"]});
    },
};