import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "../components"
import "../components/table"

Item {
    id: root

    required property var viewModel
    property color panelColor: "#151e29"
    property color borderColor: "#2B3A52"
    property color textColor: "#ffffff"
    property var testDataColumns: [
        {
            "key": "key",
            "label": "Tr\u01b0\u1eddng",
            "width": 260
        },
        {
            "key": "value",
            "label": "Gi\u00e1 tr\u1ecb",
            "type": "input",
            "stretch": true
        }
    ]

    Rectangle {
        anchors.fill: parent
        color: root.panelColor
        radius: 12
        border.color: root.borderColor

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 12

            Label {
                text: "D\u1eef li\u1ec7u in th\u1eed"
                color: root.textColor
                font.pixelSize: 18
                font.bold: true
            }

            DataTable {
                id: testDataTable
                Layout.fillWidth: true
                Layout.preferredHeight: Math.min(420, implicitHeight)
                title: "Gi\u00e1 tr\u1ecb tem"
                columns: root.testDataColumns
                rows: root.viewModel.test_rows
                rowHeight: 48
                maxVisibleRows: 8
                minimumTableBodyRows: 3
                defaultColumnWidth: 180
                tableTitleFontSize: 16
                onCellValueChanged: function(rowData, columnKey, value) {
                    root.viewModel.update_test_cell(
                        String(rowData.key),
                        columnKey,
                        String(value)
                    )
                }

                Item {
                    Layout.fillWidth: true
                }

                CustomButton {
                    text: "Xu\u1ea5t ZPL th\u1eed"
                    iconSize: 30
                    iconSource: "qrc:/icon_print"
                    onClicked: root.viewModel.print_test()
                }
            }

            Label {
                text: "Xem tr\u01b0\u1edbc ZPL"
                color: root.textColor
                font.pixelSize: 16
                font.bold: true
            }

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "#0b1220"
                radius: 4
                border.color: root.borderColor

                ScrollView {
                    anchors.fill: parent
                    anchors.margins: 12

                    TextArea {
                        text: root.viewModel.raw_zpl_preview
                        readOnly: true
                        selectByMouse: true
                        wrapMode: TextEdit.NoWrap
                        color: "#d0d5dd"
                        font.family: "Consolas"
                        font.pixelSize: 13
                        background: null
                    }
                }
            }
        }
    }
}
