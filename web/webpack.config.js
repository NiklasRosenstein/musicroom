var path = require('path');
var webpack = require('webpack');

module.exports = {
  entry: './src/app.js',
  output: { path: __dirname + '/../musicroom/static/', filename: 'bundle.js' },
  module: {
    loaders: [
      {
        test: /\.jsx?$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
        query: {
          presets: ['es2016', 'react']
        }
      },
      { test: /\.css$/, loader: "style-loader!css-loader" },
      { test: /\.woff2?(\?v=[0-9]\.[0-9]\.[0-9])?$/, use: "url-loader" },
      { test: /\.(ttf|eot|svg|png)(\?[\s\S]+)?$/, use: 'file-loader' }
    ]
  },
};
