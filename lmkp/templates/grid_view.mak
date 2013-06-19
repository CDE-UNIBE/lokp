<%inherit file="lmkp:templates/htmlbase.mak" />

<%def name="title()">Grid View</%def>


## Start of content

<!-- Filter-area  -->
<form class="form-horizontal filter_area">
    <div class="container">
        <div class="control-group">
            <label class="control-label">Active filters</label>
            <div class="controls">
                <input type="text" id="filter1" class="filter-variable1" placeholder="A sample variable > 23">
                <span class="icon-remove1">
                    <i class="icon-remove pointer"></i>
                </span>
            </div>
        </div>
        <div class="control-group">
            <div class="controls">
                <input type="text" id="filter2" class="filter-variable2" placeholder="Another sample variable = Combodia">
                <span class="icon-remove2">
                    <i class="icon-remove pointer"></i>
                </span>
            </div>
        </div>
        <div class="control-group new-filter new-filter">
            <label class="control-label">New Filter</label>
            <div class="controls">
                <div class="btn-group">
                    <button class="btn select_btn_filter">Tagggroup</button>
                    <button class="btn select_btn_filter_right dropdown-toggle" data-toggle="dropdown">
                        <span class="caret"></span>
                    </button>
                    <ul class="dropdown-menu">
                        <li><a href="#">1</a></li>
                        <li><a href="#">2</a></li>
                        <li><a href="#">3</a></li>
                        <li><a href="#">4</a></li>
                        <li><a href="#">5</a></li>
                    </ul>
                </div>
                <div class="btn-group">
                    <button class="btn select_btn_operator">&#8804;</button>
                    <button class="btn select_btn_operator_right dropdown-toggle" data-toggle="dropdown">
                        <span class="caret"></span>
                    </button>
                    <ul class="dropdown-menu">
                        <li><a href="#">&#8805;</a></li>
                        <li><a href="#">=</a></li>
                        <li><a href="#">!=</a></li>
                    </ul>
                </div>
                <input type="text" class="filter-value" id="filter2" placeholder="Value">
                <span class="icon-add">
                    <i class="icon-plus pointer"></i>
                </span>
            </div>
        </div>
        <div class="favorite">
            <div class="btn-group favorite">
                <button class="btn btn_favorite">Favorite</button>
                <button class="btn btn_favorite_right dropdown-toggle" data-toggle="dropdown">
                    <span class="caret"></span>
                </button>
                <ul class="dropdown-menu">
                    <li><a href="#">1</a></li>
                    <li><a href="#">2</a></li>
                    <li><a href="#">3</a></li>
                    <li><a href="#">4</a></li>
                    <li><a href="#">5</a></li>
                </ul>
            </div>
        </div>
    </div>
</form>

<div class="filter_area_openclose">
    <i class="icon-double-angle-up pointer"></i>
</div>

<!-- content -->
<div class="container">
    <div class="content">
        
        <p>(Please note that this is some static sample content)</p>

        <ul class="nav nav-tabs table_tabs">
            <li class="active">
                <a href="#">Deals</a>
            </li>
            <li><a href="#">Investors</a>
            </li>
        </ul>
        <div class="table_wrapper">
            <table class="table table-hover table-self table-bordered">
                <thead>
                    <tr>
                        <th>ID
                            <div class="desc pointer" onclick="location.href='#';">_</div>
                            <div class="asc active">_</div>
                        </th>
                        <th>Negotiation Status
                            <div class="desc pointer" onclick="location.href='#';">_</div>
                            <div class="asc pointer" onclick="location.href='#';">_</div>
                        </th>
                        <th>Intended Area
                            <div class="desc pointer" onclick="location.href='#';">_</div>
                            <div class="asc pointer" onclick="location.href='#';">_</div>
                        </th>
                        <th>Intention of investment
                            <div class="desc pointer" onclick="location.href='#';">_</div>
                            <div class="asc pointer" onclick="location.href='#';">_</div>
                        </th>
                    </tr>
                <tbody>
                    <tr>
                        <td>a8724</td>
                        <td>Contract signed</td>
                        <td>123.7 ha</td>
                        <td>Unknown</td>
                    </tr>
                    <tr>
                        <td>b2679</td>
                        <td>Contract signed</td>
                        <td>23 ha</td>
                        <td>Agriculture</td>
                    </tr>
                    <tr>
                        <td>c9720</td>
                        <td>Under negotiation</td>
                        <td>8 ha</td>
                        <td>Unknown</td>
                    </tr>
                    <tr class="active-row">
                        <td>d9827</td>
                        <td>Contract signed</td>
                        <td>98 ha</td>
                        <td>Conservation</td>
                    </tr>
                    <tr>
                        <td>f98376</td>
                        <td>Under negotiation</td>
                        <td>157.23 ha</td>
                        <td>Unknown</td>
                    </tr>
                    <tr>
                        <td>g9836</td>
                        <td>Contract signed</td>
                        <td>6.87 ha</td>
                        <td>Mining</td>
                    </tr>
                    <tr>
                        <td>h98753</td>
                        <td>Contract signed</td>
                        <td>2.12 ha</td>
                        <td>Agriculture</td>
                    </tr>
                    <tr>
                        <td>i2692</td>
                        <td>Contract signed</td>
                        <td>26.42 ha</td>
                        <td>Unknown</td>
                    </tr>
                </tbody>
                <thead class="table-height">
                    <tr>
                        <th>ID</th>
                        <th>Negotiation Status</th>
                        <th>Intended Area</th>
                        <th>Intention of investment</th>
                    </tr>
            </table>
        </div>
    </div>
</div>

<div class="show-investors-wrapper">
    <div class="show-investors">
        <p>Show investors for this deal</p>
    </div>
</div>

## End of content