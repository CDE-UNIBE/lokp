<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" xmlns:tal="http://xml.zope.org/namespaces/tal">
    <head>
        <title>Merge</title>
        <meta http-equiv="Content-Type" content="text/html;charset=UTF-8"/>
        <link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/lib/extjs-4.1.1/resources/css/ext-all.css')}"></link>
        <link rel="stylesheet" type="text/css" href="${request.static_url('lmkp:static/style.css')}"></link>
        <script type="text/javascript" src="${request.static_url('lmkp:static/lib/extjs-4.1.1/ext.js')}"></script>
        <script type="text/javascript">
            Ext.Loader.setConfig({
                enabled: true,
                paths: {
                    'Ext': '/static/lib/extjs-4.1.1/src',
                    'Ext.ux': '/static/lib/extjs-4.1.1/examples/ux'
                }
            });

            Ext.require([
                'Ext.data.*',
                'Ext.grid.*',
                'Ext.ux.grid.TransformGrid'
            ]);

            Ext.onReady(function(){
                //var btn = Ext.get('create-grid');
                // Always enable the button, after a refresh some browsers
                // will remember the disabled state for us
                //btn.dom.disabled = false;

                //btn.on('click', function(){
                //  btn.dom.disabled = true;

                // create the grid
                var grid = Ext.create('Ext.ux.grid.TransformGrid', 'merge-table', {
                    stripeRows: true,
                    anchor: '100%',
                    flex: 1,
                    sortable: false,
                    margin: 5
                });
                //  grid.render(Ext.getBody());
                //});

                var viewport = Ext.create('Ext.container.Viewport',{
                    items: [grid],
                    layout: 'anchor'
                });

            });
        </script>
        <style type="text/css">
            table{

                width: 98%;
            }
            .remove {
                background-color: lightcoral;
            }
            .add {
                background-color: lightgreen;
            }
        </style>
    </head>
    <body>
        <table id="merge-table">
            <thead>
                <tr>
                    % for cell in data[0]:
                    <th>
                        <div class="${cell['class']}">
                            % for tag in cell['tags']:
                            <div>${tag['key']}: ${tag['value']}</div>
                            % endfor
                        </div>
                    </th>
                    % endfor
                </tr>
            </thead>
            <tbody>
                % for row in range(1,len(data)):
                <tr>
                    % for cell in data[row]:
                    <td>
                        <div class="${cell['class']}">
                            % for tag in cell['tags']:
                            <div>${tag['key']}: ${tag['value']}</div>
                            % endfor
                        </div>
                    </td>
                    % endfor
                </tr>
                % endfor
            </tbody>
        </table>
    </body>
</html>