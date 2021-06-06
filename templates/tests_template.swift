import XCTest
@testable import <#Target#>

class <#TestCaseName#>Tests: XCTestCase {
        
    func test<#TestName#>() {
        
        {% for test in test_gen.tests %}
        let _ = {
            let prevStateJson = "{{ test.prev_state }}"

            let actionJson = "{{ test.action }}"

            let resultStateJson = "{{ test.next_state }}"

            let state = reduce(stateFrom(json: prevStateJson), actionFrom(json: actionJson))
            let stateJson = (try? JSONEncoder().encode(state)).flatMap { String(data: $0, encoding: .utf8) }

            XCTAssert(stateJson == resultStateJson)
        }()
        {% endfor %}    
    }    
}
