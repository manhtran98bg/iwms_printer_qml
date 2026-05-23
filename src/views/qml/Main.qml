import QtQuick 2.15
import QtQuick.Controls 2.15
import "pages"

ApplicationWindow {
    id: window
    width: 980
    height: 560
    minimumWidth: 900
    minimumHeight: 520
    visible: true
    title: mainViewModel.app_title
    color: "#f5f7fa"

    PrinterPage {
        anchors.fill: parent
        viewModel: mainViewModel
    }
}
