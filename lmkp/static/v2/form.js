/**
 * This file contains functions used for the forms.
 * It namely contains custom functions for the Deform form, especially for the
 * sequences. The functions are adapted to work with the new HTML form layout
 * which differs quite a lot from the Deform's default layout.
 */

function customProcessSequenceButtons(oid_node, min_len, max_len, now_len) {
    var $ul = oid_node.children('ul');
    var $lis = $ul.children('div.formSingleSequence');
    $lis.find('.close').addClass('hide');
    $lis.removeClass('alert sequencestyle');
    oid_node.children('.deformSeqAdd').show();
    if (now_len > min_len) {
        $lis.find('.close').removeClass('hide');
        $lis.addClass('alert sequencestyle');
    }
    if (now_len >= max_len) {
        oid_node.children('.deformSeqAdd').hide();
    }
}

function customRemoveSequenceItem(clicked) {
    var $item_node = $(clicked).parent().parent().parent();
    var $oid_node = $item_node.parent().parent();
    var $before_node = $oid_node.find('.deformInsertBefore').last();
    var min_len = parseInt($before_node.attr('min_len')||'0', 10);
    var max_len = parseInt($before_node.attr('max_len')||'9999', 10);
    var now_len = parseInt($before_node.attr('now_len')||'0', 10);
    if (now_len > min_len) {
        $before_node.attr('now_len', now_len - 1);
        $item_node.remove();
        customProcessSequenceButtons($oid_node, min_len, max_len,
                                      now_len-1);
    }
    return false;
}

function customAppendSequenceItem(node) {
    var $oid_node = $(node).parent().parent().parent();
    var $proto_node = $oid_node.children('.deformProto').first();
    var $before_node = $oid_node.children('ul').first().children(
                                          '.deformInsertBefore');
    var min_len = parseInt($before_node.attr('min_len')||'0', 10);
    var max_len = parseInt($before_node.attr('max_len')||'9999', 10);
    var now_len = parseInt($before_node.attr('now_len')||'0', 10);
    if (now_len < max_len) {
        customAddSequenceItem($proto_node, $before_node);
        customProcessSequenceButtons($oid_node, min_len, max_len,
                                      now_len+1);
    }
    return false;
}

function customAddSequenceItem(protonode, before) {
    // - Clone the prototype node and add it before the "before" node.
    //   Also ensure any callbacks are run for the widget.

    // In order to avoid breaking accessibility:
    //
    // - Find each tag within the prototype node with an id
    //   that has the string ``deformField(\d+)`` within it, and modify
    //   its id to have a random component.
    // - For each label referencing an change id, change the label's
    //   for attribute to the new id.

    var fieldmatch = /deformField(\d+)/;
    var namematch = /(.+)?-[#]{3}/;
    var code = protonode.attr('prototype');
    var html = decodeURIComponent(code);
    var $htmlnode = $(html);
    var $idnodes = $htmlnode.find('[id]');
    var $namednodes = $htmlnode.find('[name]');
    var $hrefnodes = $htmlnode.find('[data-parent]');
    var genid = deform.randomString(6);
    var idmap = {};

    // replace hrefs containing ``deformField`` and their data-parent
    // attributes (these are the bootstrap accordions)

    $hrefnodes.each(function(idx, node) {
        var $node = $(node);
        var old_dp = $node.attr('data-parent');
        var new_dp = old_dp.replace(fieldmatch, "deformField$1-" + genid);
        $node.attr('data-parent', new_dp);
        var old_href = $node.attr('href');
        var new_href = old_href.replace(fieldmatch, "deformField$1-" + genid);
        $node.attr('href', new_href);
    });

    // replace ids containing ``deformField`` and associated label for=
    // items which point at them

    $idnodes.each(function(idx, node) {
        var $node = $(node);
        var oldid = $node.attr('id');
        var newid = oldid.replace(fieldmatch, "deformField$1-" + genid);
        $node.attr('id', newid);
        idmap[oldid] = newid;
        var labelselector = 'label[for=' + oldid + ']';
        var $fornodes = $htmlnode.find(labelselector);
        $fornodes.attr('for', newid);
    });

    // replace names a containing ``deformField`` like we do for ids

    $namednodes.each(function(idx, node) {
        var $node = $(node);
        var oldname = $node.attr('name');
        var newname = oldname.replace(fieldmatch, "deformField$1-" + genid);
        $node.attr('name', newname);
        });

    var anchorid = genid + '-anchor';
    var anchortext = '<a name="' + anchorid +'" id="' + anchorid + '"/>';

    var containernode = $('<div class="formSingleSequence">');
    containernode.append($(anchortext));
    containernode.append($htmlnode);
    $(containernode).insertBefore(before);

    $(deform.callbacks).each(function(num, item) {
        var oid = item[0];
        var callback = item[1];
        var newid = idmap[oid];
        if (newid) {
            callback(newid);
            }
        });

    deform.clearCallbacks();
    var old_len = parseInt(before.attr('now_len')||'0', 10);
    before.attr('now_len', old_len + 1);
    //deform.maybeScrollIntoView('#' + anchorid);
}

function toggleConfirmDelete() {
    var confirm_div = $('.delete-confirm');
    var btn = $('.form-button-delete').parent('ul');
    if (confirm_div.is(':visible')) {
        confirm_div.hide();
        btn.show();
    } else {
        confirm_div.show();
        btn.hide();
    }
}
