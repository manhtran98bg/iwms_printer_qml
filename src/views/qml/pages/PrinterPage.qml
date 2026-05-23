import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Dialogs
import QtQuick.Layouts 1.15
import "../components"
import "../components/table"

Item {
    id: root

    required property var viewModel
    property string clockText: Qt.formatDateTime(new Date(), "yyyy-MM-dd hh:mm")
    property color pageColor: "#0d141d"
    property color panelColor: "#151e29"
    property color panelAltColor: "#101923"
    property color panelHoverColor: "#1b2735"
    property color borderColor: "#2B3A52"
    property color textColor: "#ffffff"
    property color mutedTextColor: "#70839b"
    property color accentColor: "#2081ef"
    property color successColor: "#22c55e"
    property color dangerColor: "#ef4444"
    property var testDataColumns: [
        {
            "key": "field",
            "label": "Field",
            "width": 150
        },
        {
            "key": "label1",
            "label": "Label 1",
            "type": "input",
            "stretch": true
        },
        {
            "key": "label2",
            "label": "Label 2",
            "type": "input",
            "stretch": true
        }
    ]

    Rectangle {
        anchors.fill: parent
        color: root.pageColor
        z: -1
    }

    Timer {
        interval: 30000
        running: true
        repeat: true
        onTriggered: root.clockText = Qt.formatDateTime(new Date(), "yyyy-MM-dd hh:mm")
    }

    FileDialog {
        id: templateDialog
        title: "Select ZPL or PRN template"
        nameFilters: ["Template files (*.zpl *.prn *.txt)", "All files (*)"]
        onAccepted: root.viewModel.set_template_path(String(selectedFile))
    }

    FileDialog {
        id: formatDialog
        title: "Select format or schema JSON"
        nameFilters: ["JSON files (*.json)", "All files (*)"]
        onAccepted: root.viewModel.set_data_path(String(selectedFile))
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        // Header section
        Rectangle {
            Layout.fillWidth: true
            height: 66
            color: root.panelColor
            border.color: root.borderColor

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 22
                anchors.rightMargin: 22
                spacing: 16

                Label {
                    Layout.fillWidth: true
                    text: "iWMS Auto Print"
                    font.pixelSize: 24
                    font.bold: true
                    color: root.textColor
                }

                Rectangle {
                    implicitWidth: apiBadgeContent.implicitWidth + 22
                    implicitHeight: 30
                    radius: 15
                    color: root.viewModel.api_running ? "#052e1a" : "#3a1014"
                    border.color: root.viewModel.api_running ? "#166534" : "#991b1b"

                    Row {
                        id: apiBadgeContent
                        anchors.centerIn: parent
                        spacing: 8

                        Rectangle {
                            width: 8
                            height: 8
                            radius: 4
                            anchors.verticalCenter: parent.verticalCenter
                            color: root.viewModel.api_running ? root.successColor : root.dangerColor
                        }

                        Label {
                            text: root.viewModel.api_running ? "API Running" : "API Stopped"
                            color: root.viewModel.api_running ? "#86efac" : "#fca5a5"
                            font.pixelSize: 13
                            font.bold: true
                        }
                    }
                }
            }
        }

        TouchScrollView {
            Layout.fillWidth: true
            Layout.fillHeight: true
            contentMinimumWidth: 860
            margins: 20
            spacing: 14

                    // API server section
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: apiPanelLayout.implicitHeight + 32
                        color: root.panelColor
                        radius: 12
                        border.color: root.borderColor

                        ColumnLayout {
                            id: apiPanelLayout
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 12

                            Label {
                                text: "API Server"
                                color: root.textColor
                                font.pixelSize: 18
                                font.bold: true
                            }

                            GridLayout {
                                Layout.fillWidth: true
                                columns: 3
                                columnSpacing: 12
                                rowSpacing: 10

                                Label {
                                    text: "URL"
                                    color: root.textColor
                                    font.pixelSize: 13
                                }

                                CustomTextBox {
                                    Layout.fillWidth: true
                                    text: root.viewModel.api_url
                                    enabled: !root.viewModel.api_running
                                    onEditingFinished: root.viewModel.set_api_url(text)
                                }

                                BaseButton {
                                    Layout.preferredWidth: 128
                                    text: root.viewModel.api_running ? "Stop Server" : "Start Server"
                                    variant: root.viewModel.api_running ? "danger" : "primary"
                                    onClicked: root.viewModel.api_running
                                        ? root.viewModel.stop_api()
                                        : root.viewModel.start_api()
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 24

                                Column {
                                    Layout.preferredWidth: 190
                                    spacing: 3

                                    Label {
                                        text: "Last request"
                                        color: root.mutedTextColor
                                        font.pixelSize: 12
                                    }

                                    Label {
                                        width: parent.width
                                        text: root.viewModel.last_request_at
                                        color: root.accentColor
                                        font.pixelSize: 18
                                        font.bold: true
                                        elide: Text.ElideRight
                                    }
                                }

                                Column {
                                    Layout.preferredWidth: 130
                                    spacing: 3

                                    Label {
                                        text: "Status"
                                        color: root.mutedTextColor
                                        font.pixelSize: 12
                                    }

                                    Label {
                                        width: parent.width
                                        text: root.viewModel.last_request_status
                                        color: root.viewModel.last_request_status.indexOf("400") >= 0 ? "#fca5a5" : "#86efac"
                                        font.pixelSize: 18
                                        font.bold: true
                                        elide: Text.ElideRight
                                    }
                                }

                                Column {
                                    Layout.preferredWidth: 130
                                    spacing: 3

                                    Label {
                                        text: "Requests"
                                        color: root.mutedTextColor
                                        font.pixelSize: 12
                                    }

                                    Label {
                                        width: parent.width
                                        text: String(root.viewModel.request_count)
                                        color: root.accentColor
                                        font.pixelSize: 18
                                        font.bold: true
                                        elide: Text.ElideRight
                                    }
                                }

                                Column {
                                    Layout.preferredWidth: 120
                                    spacing: 3

                                    Label {
                                        text: "Failed"
                                        color: root.mutedTextColor
                                        font.pixelSize: 12
                                    }

                                    Label {
                                        width: parent.width
                                        text: String(root.viewModel.failed_count)
                                        color: root.viewModel.failed_count > 0 ? "#fca5a5" : "#86efac"
                                        font.pixelSize: 18
                                        font.bold: true
                                        elide: Text.ElideRight
                                    }
                                }

                                Item {
                                    Layout.fillWidth: true
                                }
                            }
                        }
                    }

                    // Print setup section
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: setupPanelLayout.implicitHeight + 32
                        color: root.panelColor
                        radius: 12
                        border.color: root.borderColor

                        ColumnLayout {
                            id: setupPanelLayout
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 12

                            Label {
                                text: "Print Setup"
                                color: root.textColor
                                font.pixelSize: 18
                                font.bold: true
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 12

                                Label {
                                    Layout.preferredWidth: 110
                                    text: "Printer"
                                    color: root.textColor
                                    font.pixelSize: 13
                                }

                                CustomComboBox {
                                    id: printerCombo
                                    Layout.fillWidth: true
                                    model: root.viewModel.printers

                                    Component.onCompleted: {
                                        var selectedIndex = root.viewModel.printers.indexOf(root.viewModel.printer_name)
                                        if (selectedIndex >= 0) {
                                            currentIndex = selectedIndex
                                        }
                                    }

                                    Connections {
                                        target: root.viewModel

                                        function onPrintersChanged() {
                                            var selectedIndex = root.viewModel.printers.indexOf(root.viewModel.printer_name)
                                            printerCombo.currentIndex = selectedIndex >= 0 ? selectedIndex : -1
                                        }

                                        function onConfigChanged() {
                                            var selectedIndex = root.viewModel.printers.indexOf(root.viewModel.printer_name)
                                            if (selectedIndex >= 0) {
                                                printerCombo.currentIndex = selectedIndex
                                            }
                                        }
                                    }

                                    onActivated: root.viewModel.set_printer_name(currentText)
                                }

                                CustomButton {
                                    Layout.preferredWidth: 96
                                    text: "Refresh"
                                    iconSource: "qrc:/icon_refresh"
                                    onClicked: root.viewModel.refresh_printers()
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 12

                                Label {
                                    Layout.preferredWidth: 110
                                    text: "Template"
                                    color: root.textColor
                                    font.pixelSize: 13
                                }

                                CustomTextBox {
                                    Layout.fillWidth: true
                                    text: root.viewModel.template_path
                                    readOnly: true
                                    placeholderText: "No file selected"
                                }

                                CustomButton {
                                    Layout.preferredWidth: 96
                                    text: "Browse"
                                    iconSource: "qrc:/icon_browse"
                                    onClicked: templateDialog.open()
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 12

                                Label {
                                    Layout.preferredWidth: 110
                                    text: "Format"
                                    color: root.textColor
                                    font.pixelSize: 13
                                }

                                CustomTextBox {
                                    Layout.fillWidth: true
                                    text: root.viewModel.data_path
                                    readOnly: true
                                    placeholderText: "No file selected"
                                }

                                CustomButton {
                                    Layout.preferredWidth: 96
                                    text: "Browse"
                                    iconSource: "qrc:/icon_browse"
                                    onClicked: formatDialog.open()
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                spacing: 12

                                Label {
                                    Layout.preferredWidth: 110
                                    text: "Stamp columns"
                                    color: root.textColor
                                    font.pixelSize: 13
                                }

                                SpinBox {
                                    from: 1
                                    to: 8
                                    value: root.viewModel.stamp_columns
                                    onValueModified: root.viewModel.set_stamp_columns(value)
                                }

                                BaseButton {
                                    text: "Reload Format"
                                    variant: "outline"
                                    onClicked: root.viewModel.reload_format()
                                }

                                Item {
                                    Layout.fillWidth: true
                                }
                            }
                        }
                    }

                    // Test data section
                    Rectangle {
                        Layout.fillWidth: true
                        implicitHeight: testPanelLayout.implicitHeight + 32
                        color: root.panelColor
                        radius: 12
                        border.color: root.borderColor

                        ColumnLayout {
                            id: testPanelLayout
                            anchors.fill: parent
                            anchors.margins: 16
                            spacing: 12

                            Label {
                                text: "Test Data"
                                color: root.textColor
                                font.pixelSize: 18
                                font.bold: true
                            }

                            TabBar {
                                id: testTabs
                                Layout.fillWidth: true

                                TabButton { text: "Test Data" }
                                TabButton { text: "Request Log" }
                                TabButton { text: "Raw ZPL Preview" }
                            }

                            StackLayout {
                                Layout.fillWidth: true
                                currentIndex: testTabs.currentIndex

                                // Test data table section
                                Item {
                                    implicitHeight: testDataTable.implicitHeight

                                    ColumnLayout {
                                        anchors.fill: parent
                                        spacing: 12

                                        DataTable {
                                            id: testDataTable
                                            Layout.fillWidth: true
                                            title: "Label Values"
                                            columns: root.testDataColumns
                                            rows: root.viewModel.test_rows
                                            rowHeight: 48
                                            maxVisibleRows: 6
                                            minimumTableBodyRows: 3
                                            defaultColumnWidth: 180
                                            tableTitleFontSize: 16
                                            onCellValueChanged: function(rowData, columnKey, value) {
                                                root.viewModel.update_test_cell(
                                                    String(rowData.field),
                                                    columnKey,
                                                    String(value)
                                                )
                                            }
                                            Item{
                                                Layout.fillWidth: true
                                            }
                                            CustomButton {
                                                text: "Print Test"
                                                iconSize: 30
                                                iconSource:"qrc:/icon_print"
                                                onClicked: root.viewModel.print_test()
                                            }
                                        }
                                    }
                                }

                                // Request log section
                                Rectangle {
                                    implicitHeight: 210
                                    color: root.panelAltColor
                                    border.color: root.borderColor

                                    Label {
                                        anchors.centerIn: parent
                                        text: "No request log yet"
                                        color: root.mutedTextColor
                                    }
                                }

                                // Raw ZPL preview section
                                Rectangle {
                                    implicitHeight: 230
                                    color: "#0b1220"
                                    radius: 4

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
        }

        // Status bar section
        Rectangle {
            Layout.fillWidth: true
            height: 38
            color: root.panelColor
            border.color: root.borderColor

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 16
                spacing: 10

                Label {
                    Layout.fillWidth: true
                    text: root.viewModel.status
                    color: root.viewModel.api_running ? "#86efac" : root.textColor
                    elide: Text.ElideRight
                }

                Label {
                    text: root.clockText
                    color: root.mutedTextColor
                }
            }
        }
    }
}
