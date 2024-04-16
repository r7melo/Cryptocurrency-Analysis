const http = require('http');
const fs = require('fs');

const server = http.createServer((req, res) => {
    if (req.method === 'POST') {
        var cryptocurrencyName = '';
        req.on('data', function(chunk) {
            cryptocurrencyName += chunk.toString();
        });
        req.on('end', function() {
            var filename = '/coinbase/' + cryptocurrencyName + '.csv';
            if (fs.existsSync(filename)) {
                fs.readFile(filename, 'utf8', function(err, data) {
                    if (err) {
                        res.writeHead(500);
                        res.end('Erro interno do servidor');
                    } else {
                        
                        var result_data = data.trim().split('\n').map(line => line.split(','))
                        var dataArray = [];
                        
                        var lines = data.trim().split('\n');
                        var headers = lines[0].split(',');
                        for (var i = 1; i < lines.length; i++) {
                            var obj = {};
                            var currentLine = lines[i].split(',');
                            for (var j = 0; j < headers.length; j++) {
                                obj[headers[j]] = currentLine[j];
                            }
                            dataArray.push(obj);
                        }
                        res.writeHead(200, {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': '*'
                        });
                        res.end(JSON.stringify(dataArray));
                    }
                });
            } else {
                res.writeHead(404);
                res.end(`Arquivo não encontrado [${filename}]`);
            }
        });
    } else {
        res.writeHead(405);
        res.end('Método não permitido');
    }
});

server.listen(8080, () => {
    console.log('Servidor rodando na porta 8080');
});
