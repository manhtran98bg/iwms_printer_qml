import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15
import "pages"

ApplicationWindow {
    id: window
    width: 980
    height: 560
    minimumWidth: 900
    minimumHeight: 520
    visible: true
    visibility: Window.Maximized
    title: mainViewModel.app_title
    color: "#0d141d"
    font.family: "Roboto"

    PrinterPage {
        anchors.fill: parent
        viewModel: mainViewModel
    }
}
