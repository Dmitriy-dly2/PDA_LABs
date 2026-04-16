<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.12/semantic.min.css"></link>
        <style>
            .main-container { padding-top: 30px; padding-bottom: 50px; }
            .stats-box { margin-bottom: 20px !important; }
            .action-button { margin-top: 30px !important; }
        </style>
    </head>
    <body>
        <div class="ui container main-container">
            <h2 class="ui header">Разметка новостей для обучения ML</h2>

            <div class="ui message info stats-box">
                <i class="info circle icon"></i>
                Вам осталось разметить: <strong>{{len(rows)}}</strong> новостей.
            </div>

            <table class="ui celled table">
                <thead>
                    <tr>
                        <th>Title</th>
                        <th>Author</th>
                        <th colspan="3">Label</th>
                    </tr>
                </thead>
                <tbody>
                    %for row in rows:
                    <tr>
                        <td><a href="{{row.url}}" target="_blank">{{row.title}}</a></td>
                        <td>{{row.author}}</td>
                        
                        <td class="positive"><a href="/add_label?label=good&id={{row.id}}">Интересно</a></td>
                        <td class="active"><a href="/add_label?label=maybe&id={{row.id}}">Возможно</a></td>
                        <td class="negative"><a href="/add_label?label=never&id={{row.id}}">Не интересно</a></td>
                    </tr>
                    %end
                </tbody>
            </table>

            <div class="action-button">
                <a href="/recommendations" class="ui huge primary fluid button">
                    <i class="magic icon"></i> Подобрать рекомендации
                </a>
                <p style="text-align: center; color: gray; margin-top: 10px;">
                    * Нажмите после того, как разметите достаточное количество новостей
                </p>
            </div>

        </div>
    </body>
</html>