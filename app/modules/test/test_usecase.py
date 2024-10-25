from flask import render_template, Response

from app.shared.singletons.logger import Logger


class TestUseCase:
    def __init__(self):
        self.logger = Logger()

    def execute(self):
        try:
            self.logger.log(message='MinionSys online!')

            html_content =  '''
                <!DOCTYPE html>
                <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Home Page</title>
                    </head>
                    <body>
                        <h1>Online</h1>
                    </body>
                </html> 
            '''

            return Response(html_content, mimetype='text/html')

        except Exception as exc:
            self.logger.log(message=str(exc), level='error')

            return {
                'status': False,
                'message': str(exc),
                'result': None,
                'code': 500
            }
