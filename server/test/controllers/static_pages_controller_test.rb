require 'test_helper'

class StaticPagesControllerTest < ActionController::TestCase
  test "should get enter" do
    get :enter
    assert_response :success
  end

  test "should get registration" do
    get :registration
    assert_response :success
  end

  test "should get admin" do
    get :admin
    assert_response :success
  end

  test "should get profile" do
    get :profile
    assert_response :success
  end

end
