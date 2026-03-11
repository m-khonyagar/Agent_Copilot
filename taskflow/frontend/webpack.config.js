const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");

module.exports = (env, argv) => {
  const isDevelopment = argv.mode === "development";

  return {
    entry: "./src/index.js",
    output: {
      path: path.resolve(__dirname, "dist"),
      filename: isDevelopment ? "[name].js" : "[name].[contenthash].js",
      publicPath: "/",
      clean: true,
    },
    resolve: {
      extensions: [".js", ".jsx"],
    },
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          use: {
            loader: "babel-loader",
            options: {
              presets: [
                ["@babel/preset-env", { targets: "defaults" }],
                ["@babel/preset-react", { runtime: "automatic" }],
              ],
            },
          },
        },
        {
          test: /\.css$/,
          use: [
            isDevelopment ? "style-loader" : MiniCssExtractPlugin.loader,
            "css-loader",
            "postcss-loader",
          ],
        },
      ],
    },
    plugins: [
      new HtmlWebpackPlugin({
        template: "./public/index.html",
        filename: "index.html",
      }),
      ...(isDevelopment
        ? []
        : [new MiniCssExtractPlugin({ filename: "[name].[contenthash].css" })]),
    ],
    devServer: {
      historyApiFallback: true,
      port: 3000,
      hot: true,
      proxy: [
        {
          context: ["/api", "/ws"],
          target: "http://localhost:8000",
          ws: true,
          changeOrigin: true,
        },
      ],
    },
  };
};
