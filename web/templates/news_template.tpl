<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="//cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.12/semantic.min.css"></link>
    </head>
    <body>
        <div class="ui container" style="padding-top: 10px;">
        <table class="ui celled table">
            <thead><th>Title</th><th>Author</th><th colspan="3">Label</th></thead>
            <tbody>
                %for row in rows:
                <tr>
                    <td><a href="{{row.url}}">{{row.title}}</a></td>
                    <td>{{row.author}}</td>
                    <td class="positive"><a href="/add_label?label=good&id={{row.id}}">Интересно</a></td>
                    <td class="active"><a href="/add_label?label=maybe&id={{row.id}}">Возможно</a></td>
                    <td class="negative"><a href="/add_label?label=never&id={{row.id}}">Не интересно</a></td>
                </tr>
                %end
            </tbody>
        </table>
        </div>
    </body>
</html>
"""