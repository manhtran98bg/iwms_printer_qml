import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "TableLayout.js" as TableLayout

Rectangle {
    id: root

    default property alias headerActions: headerActions.data
    property string title: ""
    property var columns: []
    property var rows: []
    property int rowHeight: 40
    property int maxVisibleRows: 10
    property int defaultColumnWidth: 140
    property string viewActionText: "View"
    property string executeActionText: "Execute"
    property string removeActionText: "Remove"
    property int tableTitleFontSize: 16
    property int minimumTableBodyRows: 1
    property color titleColor: "#ffffff"
    property color frameColor: "#151e29"
    property color frameBorderColor: "#2B3A52"
    property color headerColor: "#1b2735"
    property color headerBorderColor: "#2B3A52"
    property color headerTextColor: "#ffffff"
    property color rowColor: "#121b26"
    property color alternateRowColor: "#172231"
    property color emptyRowColor: "#121b26"
    property color cellBorderColor: "#2B3A52"
    property color cellTextColor: "#ffffff"
    property color emptyTextColor: "#70839b"
    property color inputBackgroundColor: "#101923"
    property color inputBorderColor: "#2B3A52"
    property color popupBackgroundColor: "#151e29"

    signal viewRequested(var rowData)
    signal executeRequested(var rowData)
    signal removeRequested(var rowData)
    signal editorFocused
    signal editorBlurred
    signal cellValueChanged(var rowData, string columnKey, var value)

    color: "transparent"
    implicitHeight: headerRow.implicitHeight + root.desiredTableFrameHeight() + 4

    function columnWidth(column) {
        return TableLayout.columnWidth(column, defaultColumnWidth);
    }

    function stretchCount() {
        return TableLayout.stretchCount(columns);
    }

    function columnCanStretch(column) {
        return TableLayout.columnCanStretch(columns, column);
    }

    function baseTotalWidth() {
        return TableLayout.baseTotalWidth(columns, defaultColumnWidth);
    }

    function availableWidth() {
        return TableLayout.availableWidth(root.width, columns, defaultColumnWidth);
    }

    function totalWidth() {
        return TableLayout.totalWidth(root.width, columns, defaultColumnWidth);
    }

    function resolvedColumnWidth(column) {
        return TableLayout.resolvedColumnWidth(root.width, columns, defaultColumnWidth, column);
    }

    function desiredTableFrameHeight() {
        return 42 + Math.max(1, Math.min(root.rows.length, root.maxVisibleRows)) * root.rowHeight + 18;
    }

    function minimumTableFrameHeight() {
        return 42 + Math.max(1, root.minimumTableBodyRows) * root.rowHeight + 18;
    }

    function availableTableFrameHeight() {
        if (root.height <= 0) {
            return desiredTableFrameHeight();
        }
        return Math.max(minimumTableFrameHeight(), root.height - headerRow.implicitHeight - 12);
    }

    function tableFrameHeight() {
        return Math.min(desiredTableFrameHeight(), availableTableFrameHeight());
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 8

        RowLayout {
            id: headerRow
            Layout.fillWidth: true
            Layout.preferredHeight: 44
            spacing: 10

            Text {
                Layout.fillWidth: false
                Layout.minimumWidth: 150
                Layout.preferredWidth: 250
                text: root.title
                color: root.titleColor
                font.pixelSize: root.tableTitleFontSize
                font.bold: true
                elide: Text.ElideRight
            }

            RowLayout {
                id: headerActions
                Layout.fillWidth: true
                spacing: 8
                
            }
        }

        Rectangle {
            id: tableFrame
            Layout.fillWidth: true
            Layout.preferredHeight: root.tableFrameHeight()
            Layout.maximumHeight: root.tableFrameHeight()
            color: root.frameColor
            radius: 5
            border.color: root.frameBorderColor
            border.width: 1
            clip: true
            implicitHeight: root.desiredTableFrameHeight()

            Flickable {
                id: tableFlick
                anchors.fill: parent
                anchors.margins: 1
                clip: true
                contentWidth: tableContent.width
                contentHeight: tableContent.height
                boundsBehavior: Flickable.StopAtBounds
                flickableDirection: Flickable.HorizontalAndVerticalFlick
                interactive: true

                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }

                ScrollBar.horizontal: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }

                Column {
                    id: tableContent
                    width: root.totalWidth()

                    Row {
                        id: columnHeader
                        height: 42

                        Repeater {
                            model: root.columns

                            delegate: Rectangle {
                                property var columnData: modelData

                                width: root.resolvedColumnWidth(columnData)
                                height: columnHeader.height
                                color: root.headerColor
                                border.color: root.headerBorderColor

                                Text {
                                    anchors.fill: parent
                                    anchors.leftMargin: 12
                                    anchors.rightMargin: 12
                                    text: columnData.label
                                    color: root.headerTextColor
                                    font.pixelSize: 14
                                    font.bold: true
                                    verticalAlignment: Text.AlignVCenter
                                    horizontalAlignment: Text.AlignHCenter
                                    elide: Text.ElideRight
                                }
                            }
                        }
                    }

                    Repeater {
                        model: root.rows.length > 0 ? root.rows : [
                            {}
                        ]

                        delegate: Row {
                            id: bodyRow
                            property var rowData: modelData
                            property bool emptyRow: root.rows.length === 0
                            property int rowIndex: index

                            height: root.rowHeight

                            Repeater {
                                model: root.columns

                                delegate: DataTableCell {
                                    property var tableColumnData: modelData

                                    width: root.resolvedColumnWidth(tableColumnData)
                                    rowData: bodyRow.rowData
                                    columnData: tableColumnData
                                    columnIndex: index
                                    rowIndex: bodyRow.rowIndex
                                    emptyRow: bodyRow.emptyRow
                                    rowHeight: root.rowHeight
                                    viewActionText: root.viewActionText
                                    executeActionText: root.executeActionText
                                    removeActionText: root.removeActionText
                                    rowColor: root.rowColor
                                    alternateRowColor: root.alternateRowColor
                                    emptyRowColor: root.emptyRowColor
                                    borderColor: root.cellBorderColor
                                    textColor: root.cellTextColor
                                    emptyTextColor: root.emptyTextColor
                                    inputBackgroundColor: root.inputBackgroundColor
                                    inputBorderColor: root.inputBorderColor
                                    popupBackgroundColor: root.popupBackgroundColor

                                    onViewRequested: function (rowData) {
                                        root.viewRequested(rowData);
                                    }
                                    onExecuteRequested: function (rowData) {
                                        root.executeRequested(rowData);
                                    }
                                    onRemoveRequested: function (rowData) {
                                        root.removeRequested(rowData);
                                    }
                                    onEditorFocused: root.editorFocused()
                                    onEditorBlurred: root.editorBlurred()
                                    onCellValueChanged: function (rowData, columnKey, value) {
                                        root.cellValueChanged(rowData, columnKey, value);
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
