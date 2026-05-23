import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    required property var viewModel

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 14

        Label {
            text: "iWMS Auto Print"
            font.pixelSize: 24
            font.bold: true
            color: "#182230"
        }

        GridLayout {
            Layout.fillWidth: true
            columns: 3
            columnSpacing: 10
            rowSpacing: 10

            Label { text: "API URL" }
            TextField {
                Layout.fillWidth: true
                text: viewModel.api_url
                readOnly: true
            }
            Button {
                text: viewModel.api_running ? "Stop" : "Start"
                onClicked: viewModel.api_running ? viewModel.stop_api() : viewModel.start_api()
            }

            Label { text: "Template" }
            TextField {
                Layout.fillWidth: true
                text: viewModel.template_path
                readOnly: true
            }
            Button { text: "Browse" }

            Label { text: "Format" }
            TextField {
                Layout.fillWidth: true
                text: viewModel.data_path
                readOnly: true
            }
            Button { text: "Browse" }

            Label { text: "Printer" }
            ComboBox {
                Layout.fillWidth: true
                model: viewModel.printers
            }
            Button {
                text: "Refresh"
                onClicked: viewModel.refresh_printers()
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#ffffff"
            border.color: "#d0d5dd"
            radius: 6

            Label {
                anchors.centerIn: parent
                text: "Test data grid placeholder"
                color: "#667085"
            }
        }

        Label {
            Layout.fillWidth: true
            text: viewModel.status
            color: viewModel.api_running ? "#027a48" : "#344054"
        }
    }
}
