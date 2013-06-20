<div class="row-fluid">
    <div class="form-remove-more-icon">
        <span class="red pointer deformCloseButton"
              id="${field.oid}-close"
              onClick="javascript:customRemoveSequenceItem(this);"
        >
        </span>
    </div>
</div>

${field.serialize(cstruct=cstruct)}