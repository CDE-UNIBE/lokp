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
		border:1px solid #000;
		border-collapse: collapse;
		font-family:arial,sans-serif;
                width: 80%;
            }
            th {
                background: #aaa;
            }
            td,th{
		border: 1px solid #000;
		border-collapse: collapse;
		padding: 5px;
            }
            td.even {
                background: #eee;
            }
            -->
        </style>

    </head>
    <body>
        <table>
            <%

            from shapely import wkb

            attributes = ['id', 'timestamp', 'activity_identifier', 'version', 'geometry']

            nbrFeatures = 0

            for obj in result:
                for key in obj.__dict__:
                    if key not in attributes and key != '_labels':
                        if obj.__dict__[key] is not None:
                            attributes.append(key)

            %>
            <tr>
                % for a in range(0,len(attributes)):
                <th>
                    ${attributes[a]}
                </th>
                % endfor
            </tr>

            % for row in result:
            <tr>
                % for key in attributes:
                <%
                if nbrFeatures % 2 == 0:
                    c = "odd"
                else:
                    c = "even"

                value = None
                try:
                    value = str(row.__dict__[key])
                except:
                    try:
                        value = wkb.loads(str(row.__dict__[key].geom_wkb)).wkt
                    except:
                        pass
                %>
                <td class="${c}">${value}</td>
                % endfor
            </tr>
            <%
            # Count the number of features
            nbrFeatures += 1
            %>
            % endfor
        </table>
        <div>

            Number of features found: ${nbrFeatures}

        </div>
    </body>
</html>
