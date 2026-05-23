import QtQuick 2.15

Rectangle {
    id: cell

    property var rowData
    property var columnData
    property int columnIndex: 0
    property int rowIndex: 0
    property bool emptyRow: false
    property int rowHeight: 40
    property string viewActionText: "View"
    property string executeActionText: "Execute"
    property string removeActionText: "Remove"
    property string cellType: columnData && columnData.type ? columnData.type : "text"
    property string cellInputMode: columnData && columnData.inputMode ? columnData.inputMode : "text"
    property color rowColor: "#121b26"
    property color alternateRowColor: "#172231"
    property color emptyRowColor: "#121b26"
    property color borderColor: "#2B3A52"
    property color textColor: "#ffffff"
    property color emptyTextColor: "#70839b"
    property color inputBackgroundColor: "#101923"
    property color inputBorderColor: "#2B3A52"
    property color popupBackgroundColor: "#151e29"

    signal viewRequested(var rowData)
    signal executeRequested(var rowData)
    signal removeRequested(var rowData)
    signal editorFocused()
    signal editorBlurred()
    signal cellValueChanged(var rowData, string columnKey, var value)

    height: rowHeight
    color: emptyRow ? emptyRowColor : (rowIndex % 2 === 0 ? rowColor : alternateRowColor)
    border.color: borderColor

    function valueFor(row, column, columnIndex) {
        if (!row || !column) {
            return "";
        }
        if (Array.isArray(row)) {
            return row[columnIndex] || "";
        }
        var value = row[column.key];
        return value === undefined || value === null || value === "" ? "---" : String(value);
    }

    function editValueFor(row, column, columnIndex) {
        if (!row || !column) {
            return "";
        }
        if (Array.isArray(row)) {
            return row[columnIndex] === undefined || row[columnIndex] === null ? "" : String(row[columnIndex]);
        }
        var value = row[column.key];
        return value === undefined || value === null ? "" : String(value);
    }

    function rowOptions() {
        if (!columnData) {
            return [];
        }
        if (rowData && columnData && rowData[columnData.key + "Options"]) {
            return rowData[columnData.key + "Options"];
        }
        return columnData.options || [];
    }

    function isMultiValueCell() {
        return rowData && columnData && rowData[columnData.key + "Multi"] === true;
    }

    function selectedValues() {
        if (rowData && columnData && Array.isArray(rowData[columnData.key + "Values"])) {
            return rowData[columnData.key + "Values"].slice();
        }
        var value = valueFor(rowData, columnData, columnIndex);
        return value === "---" ? [] : value.split(",").map(function(item) {
            return item.trim();
        }).filter(function(item) {
            return item.length > 0;
        });
    }

    function toggleSelectedValue(value, checked) {
        if (!columnData) {
            return;
        }
        var values = selectedValues();
        var indexOfValue = -1;
        for (var i = 0; i < values.length; i += 1) {
            if (String(values[i]) === String(value)) {
                indexOfValue = i;
                break;
            }
        }

        if (checked && indexOfValue < 0) {
            values.push(String(value));
        } else if (!checked && indexOfValue >= 0) {
            values.splice(indexOfValue, 1);
        }
        cellValueChanged(rowData, columnData.key, values.join("\u001f"));
    }

    function selectedDisplayText() {
        var values = selectedValues();
        return values.length > 0 ? values.join(", ") : "---";
    }

    TableTextCell {
        visible: cellType !== "actions" && cellType !== "input" && cellType !== "combo" && cellType !== "remove"
        displayText: cell.valueFor(cell.rowData, cell.columnData, cell.columnIndex)
        emptyRow: cell.emptyRow
        textColor: cell.textColor
        emptyTextColor: cell.emptyTextColor
    }

    TableInputCell {
        visible: cellType === "input" && !cell.emptyRow
        textValue: cell.editValueFor(cell.rowData, cell.columnData, cell.columnIndex)
        inputMode: cell.cellInputMode
        rowHeight: cell.rowHeight
        textColor: cell.textColor
        backgroundColor: cell.inputBackgroundColor
        borderColor: cell.inputBorderColor
        onEditorFocused: cell.editorFocused()
        onEditorBlurred: cell.editorBlurred()
        onValueCommitted: function(value) {
            cell.cellValueChanged(cell.rowData, cell.columnData.key, value);
        }
    }

    TableComboCell {
        visible: cellType === "combo" && !cell.emptyRow && !cell.isMultiValueCell()
        options: cell.rowOptions()
        currentValue: cell.valueFor(cell.rowData, cell.columnData, cell.columnIndex)
        rowHeight: cell.rowHeight
        textColor: cell.textColor
        backgroundColor: cell.inputBackgroundColor
        borderColor: cell.inputBorderColor
        popupBackgroundColor: cell.popupBackgroundColor
        onValueSelected: function(value) {
            cell.cellValueChanged(cell.rowData, cell.columnData.key, value);
        }
    }

    TableMultiSelectCell {
        visible: cellType === "combo" && !cell.emptyRow && cell.isMultiValueCell()
        options: cell.rowOptions()
        selectedValues: cell.selectedValues()
        displayText: cell.selectedDisplayText()
        rowHeight: cell.rowHeight
        popupBackgroundColor: cell.popupBackgroundColor
        onValueToggled: function(value, checked) {
            cell.toggleSelectedValue(value, checked);
        }
    }

    TableActionCell {
        visible: cellType === "actions" && !cell.emptyRow
        viewActionText: cell.viewActionText
        executeActionText: cell.executeActionText
        executeEnabled: !(cell.rowData && cell.rowData.executeDisabled === true)
        onViewRequested: cell.viewRequested(cell.rowData)
        onExecuteRequested: cell.executeRequested(cell.rowData)
    }

    TableRemoveCell {
        visible: cellType === "remove" && !cell.emptyRow
        buttonText: cell.columnData && cell.columnData.text ? cell.columnData.text : cell.removeActionText
        onRemoveRequested: cell.removeRequested(cell.rowData)
    }
}
