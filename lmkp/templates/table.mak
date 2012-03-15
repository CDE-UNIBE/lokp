<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" xmlns:tal="http://xml.zope.org/namespaces/tal">
    <head>
        <title>Table output</title>
        <style type="text/css">
            <!--
            body {
                font-family: sans-serif;
                font-size: 13px;
            }
            table {
                border-style: solid;
                width: 85%;
            }
            -->
        </style>

    </head>
    <body>
        <div>

            Number of results: ${nbr}

        </div>

        <table border="1">
            <%

            from shapely import wkb

            attributes = []

            for obj in result:
                for key in obj.__dict__:
                    if key not in attributes and key != '_labels':
                        attributes.append(key)

            %>
            <tr>
                % for a in range(0,len(attributes)):
                <td>
                    ${attributes[a]}
                </td>
                % endfor
            </tr>

            % for row in result:
            <tr>
                % for key in attributes:
                <td>
                <%
                value = None
                try:
                    value = str(row.__dict__[key])
                except:
                    try:
                        value = wkb.loads(str(row.__dict__[key].geom_wkb)).wkt
                    except:
                        pass
                %>
                ${value}
                </td>
                % endfor
            </tr>
            % endfor
        </table>
    </body>
</html>
