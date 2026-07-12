const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CopyPlugin = require("copy-webpack-plugin");

module.exports = {
  // devtool: "source-map",
  entry: path.resolve(__dirname, "src/index.js"),
  output: {
    path: path.resolve(__dirname, "dist"),
  },
  devServer: {
    port: 9000,
    // without this, doesn't reload when pug files changes
    watchFiles: "src/**/*.*",
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: ["babel-loader"],
      },
      {
        test: /\.pug$/,
        use: ["html-loader", "pug-html-loader"],
      },
      {
        test: /\.(png|jpg|gif|jpeg|svg)$/,
        type: "asset/resource",
        generator: {
          outputPath: "images/",
          publicPath: "images/",
          filename: "[name][ext]",
        },
      },
      {
        test: /\.(css|scss)$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: "css-loader",
            options: { importLoaders: 1 },
          },
          "postcss-loader",
          "sass-loader",
        ],
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: `./src/index.pug`,
    }),
    new MiniCssExtractPlugin(),
    new CopyPlugin({
      patterns: [{ from: "src/images/not-found.svg", to: "images" }],
    }),
  ],
};
