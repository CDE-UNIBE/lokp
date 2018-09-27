<div class="row-fluid">
    <div class="form-remove-more-icon">
        <span class="sequence-close close hide"
              id="${field.oid}-close"
              onClick="javascript:customRemoveSequenceItem(this);"
        >&times;</span>
    </div>
</div>

${field.serialize(cstruct=cstruct)}
